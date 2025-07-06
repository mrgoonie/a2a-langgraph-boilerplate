import pytest
import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.base import Base
from app.models import mcp_server as mcp_server_model
from app.schemas.crew import CrewCreate
from app.schemas.agent import AgentCreate
from app.schemas.tool import ToolCreate
from app.schemas.mcp_server import McpServerCreate
from app.schemas.prompt import PromptCreate
from app.services import crew as crew_service
from app.services import agent as agent_service
from app.services import tool as tool_service
from app.services import mcp_server as mcp_server_service
from app.services.crew import execute_prompt

# Load environment variables for tests
load_dotenv()

# Use an in-memory SQLite database for testing
DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Fixture to set up and tear down the database for each test function
@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


# Fixture for a simple crew with only a supervisor
@pytest.fixture(scope="function")
def simple_crew(db_session):
    crew_data = CrewCreate(name="Simple Crew")
    crew = crew_service.create_crew(db=db_session, crew=crew_data)

    supervisor = next(
        (agent for agent in crew.agents if agent.role == "supervisor"), None
    )
    assert supervisor is not None, "Supervisor not found in the created crew"
    supervisor.system_prompt = """You are a helpful assistant. If the prompt is simple, you can respond directly without delegating to any agents and then FINISH. For any other request, you must state that you cannot help and then FINISH."""
    db_session.commit()

    return crew


# Fixture for a multi-agent crew for travel advice
@pytest.fixture(scope="function")
def travel_crew(db_session):
    tavily_server = (
        db_session.query(mcp_server_model.McpServer).filter_by(name="Tavily").first()
    )
    if not tavily_server:
        tavily_server_data = McpServerCreate(
            name="Tavily", url="https://api.tavily.com", description="Tavily Search API"
        )
        tavily_server = mcp_server_service.create_mcp_server(
            db=db_session, mcp_server=tavily_server_data
        )

    crew_data = CrewCreate(name="Travel Crew")
    crew = crew_service.create_crew(db=db_session, crew=crew_data)

    supervisor = next(
        (agent for agent in crew.agents if agent.role == "supervisor"), None
    )
    assert supervisor is not None, "Supervisor not found for the travel crew"
    supervisor.system_prompt = """You are a supervisor for a travel planning crew.
Your agents are:
- Researcher: A travel expert who can find information online.

Your job is to:
1. Analyze user queries for travel advice.
2. Delegate research tasks to the 'Researcher' agent.
3. Synthesize the researcher's findings into a helpful travel plan.
4. After providing the travel plan, you must respond with FINISH.
5. If the query is not about travel, say you cannot help and then FINISH."""
    db_session.commit()

    researcher_data = AgentCreate(
        name="Researcher",
        role="researcher",
        system_prompt="You are a world-class travel researcher. You find the best information on attractions and local cuisine.",
        crew_id=crew.id,
    )
    researcher = agent_service.create_agent(db=db_session, agent=researcher_data)

    tool_data = ToolCreate(
        name="tavily_search",
        description="A tool to search the web for information.",
        agent_id=researcher.id,
        mcp_server_id=tavily_server.id,
        config={"api_key": os.getenv("TAVILY_API_KEY")},
    )
    tool_service.create_tool(db=db_session, tool=tool_data)

    return crew


def get_sender(msg):
    """Helper to get the sender from different message types."""
    if isinstance(msg, AIMessage):
        # AIMessage may have a name attribute
        return getattr(msg, "name", "supervisor")  # Default to supervisor if no name
    if isinstance(msg, HumanMessage):
        return "user"
    if isinstance(msg, dict):
        # Check various possible fields for sender info
        if msg.get("type") == "system":
            return "system"
        return msg.get("from") or msg.get("name") or msg.get("sender")
    return None


def test_simple_direct_response(db_session, simple_crew):
    """
    Test Case 1: Simple Direct Response
    - User asks "hello"
    - Supervisor should respond directly without delegation.
    """
    prompt = PromptCreate(
        crew_id=simple_crew.id, prompt="hello", user_id="test-user-simple"
    )

    final_result = execute_prompt(db=db_session, crew_id=simple_crew.id, prompt=prompt)

    assert final_result is not None
    assert "messages" in final_result
    messages = final_result["messages"]
    assert len(messages) > 0

    # Debug: Print all messages for verification
    print(f"\n=== TEST 1: Simple Direct Response ===")
    print(f"Total messages: {len(messages)}")
    for i, msg in enumerate(messages):
        sender = get_sender(msg)
        content = (
            msg.get("content", "")
            if isinstance(msg, dict)
            else getattr(msg, "content", "")
        )
        print(f"Message {i+1} - From: {sender}")
        print(f"Content: {content}")
        print("---")

    # The last message should be from the supervisor.
    last_message = messages[-1]
    assert get_sender(last_message) == "supervisor"

    content = (
        last_message.get("content", "")
        if isinstance(last_message, dict)
        else last_message.content
    )
    assert "hello" in content.lower()

    # Ensure no other agents were involved
    agent_messages = [
        m for m in messages if get_sender(m) not in ["user", "supervisor", None]
    ]
    assert (
        len(agent_messages) == 0
    ), f"Unexpected agent messages found: {[get_sender(m) for m in agent_messages]}"


def test_multi_agent_collaboration(db_session, travel_crew):
    """
    Test Case 2: Multi-Agent Collaboration
    - User asks for travel advice.
    - Supervisor delegates to Researcher.
    - Supervisor synthesizes the final response.
    """
    prompt = PromptCreate(
        crew_id=travel_crew.id,
        prompt="Give me travel advice for Nha Trang beach in Vietnam.",
        user_id="test-user-multi",
    )

    final_result = execute_prompt(db=db_session, crew_id=travel_crew.id, prompt=prompt)

    assert final_result is not None
    assert "messages" in final_result
    messages = final_result["messages"]
    assert len(messages) > 0

    # Debug: Print all messages for verification
    print(f"\n=== TEST 2: Multi-Agent Collaboration ===")
    print(f"Total messages: {len(messages)}")
    for i, msg in enumerate(messages):
        sender = get_sender(msg)
        content = (
            msg.get("content", "")
            if isinstance(msg, dict)
            else getattr(msg, "content", "")
        )
        print(f"Message {i+1} - From: {sender}")
        print(f"Content: {content}")
        print("---")

    # Check for researcher involvement
    researcher_messages = [m for m in messages if get_sender(m) == "Researcher"]
    assert len(researcher_messages) > 0, "Researcher agent was not called."

    # The last message should be from supervisor (if workflow completed normally) or system (if terminated)
    last_message = messages[-1]
    last_sender = get_sender(last_message)

    # If workflow was terminated due to max visits, we should still have researcher responses
    if last_sender == "system":
        # In this case, check that there are supervisor and researcher messages
        supervisor_messages = [m for m in messages if get_sender(m) == "supervisor"]
        assert len(supervisor_messages) > 0, "Supervisor agent was not involved."

        # Check that at least one message mentions the travel destination
        all_content = " ".join(
            [
                (m.get("content", "") if isinstance(m, dict) else m.content)
                for m in messages
                if hasattr(m, "content") or (isinstance(m, dict) and "content" in m)
            ]
        )
        assert (
            "nha trang" in all_content.lower() or "vietnam" in all_content.lower()
        ), "Travel destination not mentioned in any message"
    else:
        # Normal completion case - last message should be from supervisor
        assert last_sender == "supervisor"
        content = (
            last_message.get("content", "")
            if isinstance(last_message, dict)
            else last_message.content
        )
        assert "nha trang" in content.lower()
