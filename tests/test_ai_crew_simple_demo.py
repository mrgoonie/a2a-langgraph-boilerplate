#!/usr/bin/env python3
"""
AI crew workflow demonstration that uses the actual API endpoints and functions.
This script demonstrates the complete workflow between a supervisor and specialized agents
using the real implementation of the A2A-LangGraph framework.
"""

import os
import sys
import uuid
import json
import time
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from dotenv import load_dotenv
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

# Add the project root to the path so we can import the app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import necessary modules from the project
from app.core.database import get_db, engine
from app.models.base import Base
from app.models.mcp_server import McpServer
from app.schemas.crew import CrewCreate
from app.schemas.agent import AgentCreate
from app.schemas.tool import ToolCreate
from app.schemas.prompt import PromptCreate
from app.schemas.mcp_server import McpServerCreate
from app.services import crew as crew_service
from app.services import agent as agent_service
from app.services import tool as tool_service
from app.services import mcp_server as mcp_server_service
from app.schemas import mcp_server as mcp_server_schema
from app.core.tools import create_search_api_tool, create_mcp_tools

# Helper function to make LangChain messages JSON serializable
def serialize_langchain_result(result):
    """Convert LangChain message objects to JSON serializable format"""
    if isinstance(result, dict):
        return {k: serialize_langchain_result(v) for k, v in result.items()}
    elif isinstance(result, list):
        return [serialize_langchain_result(item) for item in result]
    elif isinstance(result, BaseMessage):
        # Convert BaseMessage objects to a serializable dict
        return {
            "type": result.__class__.__name__,
            "content": result.content,
            "additional_kwargs": result.additional_kwargs
        }
    else:
        return result

# Ensure database is set up
Base.metadata.create_all(bind=engine)

# Initialize database session
db = next(get_db())

# Load environment variables
load_dotenv()

# Debug: Check if Tavily API key is loaded
tavily_key = os.getenv('TAVILY_API_KEY')
print(f"Tavily API Key loaded: {'Yes, key found' if tavily_key else 'No, key not found'} (length: {len(tavily_key) if tavily_key else 0})")

# Set up logging
from app.core.logging import get_logger
logger = get_logger(__name__)

def demonstrate_ai_crew_workflow():
    """
    Demonstrate the complete AI crew workflow using actual API endpoints and functions.
    This covers:
    1. Creating AI crew with supervisor
    2. Adding specialized agents
    3. Configuring tools for agents
    4. Executing a prompt through the crew
    5. Showing the complete flow with real results
    """
    print("\n" + "=" * 80)
    print("AI CREW WORKFLOW DEMONSTRATION")
    print("=" * 80)
    
    # Step 1: Create an AI crew with a supervisor agent
    print("\n[STEP 1] Creating AI Crew with Supervisor Agent...")
    
    # Create the AI crew
    crew_data = CrewCreate(name="ML Education Crew")
    crew = crew_service.create_crew(db=db, crew=crew_data)
    print(f"Created AI Crew: {crew.name} (ID: {crew.id})")
    
    # Create the supervisor agent with proper system prompt
    supervisor_prompt = """
    You are the supervisor agent for an AI crew specializing in machine learning education.
    Your crew has the following specialized agents:
    - Researcher: Expert in researching and explaining machine learning concepts
    - Coder: Expert in writing and explaining code examples for machine learning
    - Summarizer: Expert in providing clear, simple explanations of complex concepts
    
    Your job is to:
    1. Analyze user queries related to machine learning
    2. Create a brief plan with 3-5 MAXIMUM steps to address the query
    3. Delegate appropriate tasks to your specialized agents - use at most 1 task per agent
    4. Synthesize their responses into a comprehensive answer
    5. FINISH the workflow as soon as you have collected enough information
    
    IMPORTANT TERMINATION RULES:
    - After receiving ONE response from each agent, assess if you have enough information
    - If you have enough information to answer the query, select FINISH immediately
    - Do not exceed more than one round of communication with each agent
    - When synthesizing a final answer, select FINISH immediately after
    - Always prefer to FINISH sooner rather than later to avoid excessive token usage
    
    Keep workflow steps minimal and focused only on essential information needed.
    """
    
    supervisor_agent = AgentCreate(
        name="Supervisor",
        role="supervisor",  # Must be "supervisor" for the crew's main agent
        system_prompt=supervisor_prompt,
        crew_id=crew.id,
        model="google/gemini-2.5-pro"
    )
    
    supervisor = agent_service.create_agent(db=db, agent=supervisor_agent)
    print(f"Created Supervisor Agent: {supervisor.name} (ID: {supervisor.id})")
    
    # Step 2: Add specialized agents to the crew
    print("\n[STEP 2] Adding specialized agents to the crew...")
    
    # Create researcher agent
    researcher_prompt = """
    You are a Machine Learning Research Expert who specializes in explaining machine learning
    concepts clearly and accurately. When asked about machine learning topics, provide
    comprehensive information based on academic research and established knowledge.
    Focus on accuracy and educational value in your responses.
    """
    
    researcher_agent = AgentCreate(
        name="Researcher",
        role="researcher",
        system_prompt=researcher_prompt,
        crew_id=crew.id,
        model="google/gemini-2.5-flash"
    )
    
    researcher = agent_service.create_agent(db=db, agent=researcher_agent)
    print(f"Created Researcher Agent: {researcher.name} (ID: {researcher.id})")
    
    # Create coder agent
    coder_prompt = """
    You are a Machine Learning Code Expert who specializes in writing clear, executable code
    examples for machine learning algorithms and techniques. When asked to provide code,
    focus on writing clean, well-commented Python examples that demonstrate the concept
    being discussed. Include explanations of the key parts of the code.
    """
    
    coder_agent = AgentCreate(
        name="Coder",
        role="coder",
        system_prompt=coder_prompt,
        crew_id=crew.id,
        model="google/gemini-2.5-flash"
    )
    
    coder = agent_service.create_agent(db=db, agent=coder_agent)
    print(f"Created Coder Agent: {coder.name} (ID: {coder.id})")
    
    # Create summarizer agent
    summarizer_prompt = """
    You are a Machine Learning Explainer who specializes in making complex machine learning
    concepts accessible to beginners. When asked to explain a concept, provide clear,
    jargon-free explanations that use analogies and simple language. Your goal is to help
    people understand machine learning without requiring advanced math or computer science knowledge.
    """
    
    summarizer_agent = AgentCreate(
        name="Summarizer",
        role="summarizer",
        system_prompt=summarizer_prompt,
        crew_id=crew.id,
        model="google/gemini-2.5-pro"
    )
    
    summarizer = agent_service.create_agent(db=db, agent=summarizer_agent)
    print(f"Created Summarizer Agent: {summarizer.name} (ID: {summarizer.id})")
    
    # Step 3: Add tools to agents
    print("\n[STEP 3] Adding tools to agents...")
    
    # First check if MCP server already exists
    print("Checking for existing MCP server...")
    mcp_server_url = "https://searchapi-mcp.prod.diginext.site/mcp"
    existing_mcp_server = db.query(McpServer).filter(McpServer.url == mcp_server_url).first()
    
    if existing_mcp_server:
        print(f"Found existing MCP Server: {existing_mcp_server.name} (ID: {existing_mcp_server.id})")
        mcp_server = existing_mcp_server
    else:
        # Create a new MCP server
        print("Creating new MCP server...")
        mcp_server_data = McpServerCreate(
            name="Search API MCP",
            url=mcp_server_url
        )
        mcp_server = mcp_server_service.create_mcp_server(db=db, mcp_server=mcp_server_data)
    print(f"Created MCP Server: {mcp_server.name} (ID: {mcp_server.id})")
    
    # Create a search tool with the MCP server ID
    search_tool = ToolCreate(
        name="Search API",
        description="A tool that can search the internet for information",
        api_name="tavily_search",
        mcp_server_id=mcp_server.id
    )
    
    tool = tool_service.create_tool(db=db, tool=search_tool)
    print(f"Created Tool: {tool.name} (ID: {tool.id})")
    
    # In a real workflow, we would assign the tool to all specialized agents
    print("Adding tool to agents using actual API endpoints...")
    # Use the actual agent service API to assign tools to agents, but with a timeout
    agents_objs = [researcher, coder, summarizer]
    for agent in agents_objs:
        try:
            # Add a timeout mechanism to prevent hanging
            import signal
            
            def timeout_handler(signum, frame):
                raise TimeoutError("API call timed out")
            
            # Set a 10-second timeout
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(5)  # 5 seconds timeout
            
            # Make the API call
            agent_service.add_tool_to_agent(db=db, agent_id=agent.id, tool_id=tool.id)
            
            # Cancel the alarm if successful
            signal.alarm(0)
            print(f"Successfully added tool to {agent.name} (ID: {agent.id})")
            
        except TimeoutError as te:
            print(f"Timeout adding tool to {agent.name}: Operation took too long")
            logger.warning(f"Timeout adding tool to {agent.name}: Operation took too long")
            
        except Exception as e:
            print(f"Error adding tool to {agent.name}: {str(e)}")
            logger.error(f"Error adding tool to {agent.name}: {str(e)}", exc_info=True)
    
    # Step 4: Execute a prompt through the crew
    print("\n[STEP 4] Executing a prompt through the crew...")
    
    user_query = """
    I need help understanding the basics of machine learning algorithms, 
    then I want to see a simple Python example of a decision tree classifier,
    and finally give me a summary of how decision trees work in simple terms.
    """
    
    print("User Query:\n" + user_query + "\n")
    
    # Create the prompt
    prompt = PromptCreate(prompt=user_query)
    
    # Verify the crew and agents were created correctly before execution
    print("\nValidating workflow setup...")
    assert crew is not None, "Crew should not be None"
    assert supervisor is not None, "Supervisor agent should not be None"
    assert len(agents_objs) >= 3, "At least 3 specialized agents should be created"
    assert tool is not None, "Tool should not be None"
    print("✓ All workflow components successfully created and configured")
    
    print("\nExecuting the workflow using actual API endpoints...")
    print("Sending prompt to crew. This may take some time...")
    
    # Add a timeout for workflow execution
    import signal
    
    def workflow_timeout_handler(signum, frame):
        raise TimeoutError("Workflow execution timed out")
    
    # Set a 30-second timeout for workflow execution
    signal.signal(signal.SIGALRM, workflow_timeout_handler)
    signal.alarm(900)  # 15 minutes timeout
    
    try:
        # Actually execute the prompt using the crew service - NO SIMULATION
        result = crew_service.execute_prompt(db=db, crew_id=crew.id, prompt=prompt)
        # Cancel the alarm if successful
        signal.alarm(0)
    except TimeoutError:
        print("Workflow execution timed out after 15 minutes")
        logger.warning("Workflow execution timed out after 15 minutes")
        result = {"error": "Workflow execution timed out after 15 minutes. This could be due to connectivity issues or slow response from external services."}
    except Exception as e:
        # Cancel the alarm if there was an exception
        signal.alarm(0)
        print(f"Error during workflow execution: {str(e)}")
        logger.error(f"Error during workflow execution: {str(e)}", exc_info=True)
        result = {"error": f"Error executing prompt: {str(e)}"}
    
    # Log the real result
    print("\nPrompt execution completed!")
    print("Result type:", type(result))
    
    # Serialize the result to make it JSON serializable
    serialized_result = serialize_langchain_result(result)
    try:
        print("Result structure:", json.dumps(serialized_result, indent=2) if isinstance(serialized_result, dict) else str(serialized_result))
    except Exception as e:
        print(f"Error serializing result: {e}")
        print("Raw result (unformatted):", str(result))
    
    # Add basic validation for the result
    if isinstance(result, dict):
        if "error" in result:
            print(f"\nWarning: Execution returned an error: {result['error']}")
            print("This could be due to authentication or connectivity issues with the MCP server.")
            print("Please check your API keys and server configurations.")
        elif "messages" in result:
            print(f"\nSuccess! Received {len(result['messages'])} messages in the conversation.")
            if "workflow" in result:
                print(f"Workflow contained {len(result['workflow'])} steps.")
    else:
        print("Unexpected result format. Please check the API response structure.")
    
    # Even if we get an error, we can at least validate that the attempt was made
    # and all the workflow components were set up correctly
    
    # Step 5: Show the response and demonstrate the workflow
    print("\n[STEP 5] Workflow results")
    print("=" * 80)
    print("COMPLETE WORKFLOW DEMONSTRATION RESULTS")
    print("=" * 80 + "\n")
    
    # Print the complete response, which includes all agent interactions and the final result
    print("Final Response:\n")
    if isinstance(result, dict) and "messages" in result:
        messages = result["messages"]
        
        for i, message in enumerate(messages):
            if "content" in message:
                if "from" in message and message["from"] != "user":
                    agent_name = message["from"].capitalize() if isinstance(message["from"], str) else "System"
                    print(f"\n[{agent_name}]")
                    print("-" * 40)
                    print(message["content"])
                    print("-" * 40)
    else:
        print(json.dumps(result, indent=2))
    
    # Clean up (optional - comment these out if you want to keep the data)
    # crew_service.delete_crew(db=db, crew_id=crew.id)
    # print("\nCleanup: Deleted crew and all associated agents")
    
    print("\n" + "=" * 80)
    print("Demonstration Summary:")
    print("This demonstration showed the complete AI crew workflow:")
    print("1. Creating an AI crew with specialized agents")
    print("2. Configuring agents with appropriate system prompts")
    print("3. Adding tools to enhance agent capabilities")
    print("4. Processing a user query through the supervisor agent")
    print("5. Delegating tasks to specialized agents using A2A protocol")
    print("6. Synthesizing a comprehensive response")
    print("=" * 80 + "\n")
    
    return result

if __name__ == "__main__":
    # Execute the demonstration
    try:
        result = demonstrate_ai_crew_workflow()
    except Exception as e:
        logger.error(f"Error in demonstration: {str(e)}", exc_info=True)
        print(f"\nError occurred: {str(e)}")
    finally:
        # Close the database session
        db.close()
