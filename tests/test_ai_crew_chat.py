import os
import sys
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langchain_core.tools import tool

# Add the project root to the path so we can import the app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.agents import create_agent, create_supervisor
from app.core.graph import AgentGraph

# Load environment variables
load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env'))

# Check if the API key is loaded
openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
if not openrouter_api_key:
    raise ValueError("OPENROUTER_API_KEY not found in environment variables. Please check your .env file.")

# Create some specialized tools for different agents
@tool
def research_tool(query: str) -> str:
    """Research tool that can find information on a topic."""
    return f"Found the following information about '{query}': This is a simulated research result."

@tool
def code_analysis_tool(code: str) -> str:
    """Analyzes code and provides feedback."""
    return f"Analysis of the code: The code is syntactically correct and follows best practices."

@tool
def summarize_tool(text: str) -> str:
    """Summarizes text to extract key points."""
    return f"Summary of the text: The key points are extracted from the provided content."


def demo_ai_crew_chat_workflow():
    """
    Test that demonstrates the AI crew chat workflow:
    1. Supervisor receives input
    2. Supervisor analyzes and creates a plan based on AI crew members' capabilities
    3. Supervisor routes tasks to appropriate agents
    4. Agents process their tasks and respond
    5. Agents communicate with each other through the supervisor
    6. Supervisor collects all results and responds to the user
    """
    # Set up the LLM with OpenRouter
    api_key = os.getenv("OPENROUTER_API_KEY")
    print(f"Using API key: {api_key[:5]}...{api_key[-4:]}")
    
    # Set up headers required for OpenRouter
    headers = {
        "HTTP-Referer": "https://localhost:5000",  # Required by OpenRouter
        "X-Title": "AI Crew Chat Test"  # Name of your application
    }
    
    llm = ChatOpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
        model="google/gemini-2.5-flash",  # Using Claude for good reasoning capabilities
        default_headers=headers
    )
    
    # Create specialized agents with different capabilities
    researcher = create_agent(
        llm, 
        [research_tool], 
        """You are the Research Agent. 
        Your specialty is finding and providing information on various topics.
        When assigned a task, thoroughly analyze what information is needed and use your research tool.
        Provide comprehensive and accurate information."""
    )
    
    coder = create_agent(
        llm, 
        [code_analysis_tool], 
        """You are the Code Agent.
        Your specialty is analyzing, writing, and improving code.
        When assigned a task related to code, carefully examine it and provide expert feedback.
        Use your code analysis tool to help with your assessment."""
    )
    
    summarizer = create_agent(
        llm, 
        [summarize_tool], 
        """You are the Summarization Agent.
        Your specialty is condensing information and extracting key points.
        When given information, identify the most important elements and create concise summaries.
        Use your summarize tool to help with this process."""
    )
    
    # Define the agents list for the supervisor
    agents = [
        {"name": "researcher", "agent": researcher},
        {"name": "coder", "agent": coder},
        {"name": "summarizer", "agent": summarizer},
    ]
    
    # Create the supervisor agent with enhanced instructions to demonstrate A2A communication
    supervisor = create_supervisor(
        llm,
        agents,
        """You are the Supervisor Agent that coordinates an AI crew.
        Your responsibilities:
        1. Analyze incoming user requests and create a detailed plan
        2. Break down complex tasks into subtasks appropriate for each specialized agent
        3. Route tasks to the appropriate agents based on their capabilities
        4. Coordinate communication between agents when they need to build on each other's work
        5. Collect results from all agents, synthesize them, and provide a comprehensive response
        
        Available agents:
        - researcher: Expert at finding information on topics
        - coder: Expert at analyzing and working with code
        - summarizer: Expert at condensing information and extracting key points
        
        For complex tasks, consider how agents can work together sequentially, with one agent's 
        output becoming another agent's input. Think carefully about task dependencies.
        """
    )
    
    # Create the agent graph with tools
    tools = [research_tool, code_analysis_tool, summarize_tool]
    graph = AgentGraph(supervisor, agents, tools)
    
    # Compile the graph
    app = graph.compile()
    
    # User query that requires multiple agents working together
    complex_query = """
    I need help understanding the basics of machine learning algorithms, 
    then I want to see a simple Python example of a decision tree classifier,
    and finally give me a summary of how decision trees work in simple terms.
    """
    
    # Execute the graph and capture all steps
    steps = []
    for step in app.stream(
        {
            "messages": [
                HumanMessage(content=complex_query)
            ]
        }
    ):
        if "__end__" not in step:
            steps.append(step)
            print(f"\n--- STEP ---\n{step}\n-----------")
    
    # Analyze the workflow
    print(f"\nWorkflow had {len(steps)} steps showing agent interactions")
    
    # Check if supervisor routed to different agents
    agent_involvement = set()
    for step in steps:
        if "next" in step and step["next"] in ["researcher", "coder", "summarizer"]:
            agent_involvement.add(step["next"])
    
    # Show which agents were involved
    print(f"Agents involved: {', '.join(agent_involvement)}")
    
    # Get final response
    final_messages = steps[-1]["messages"]
    final_response = final_messages[-1].content if final_messages else ""
    
    if final_response:
        print("\n----- FINAL RESPONSE FROM SUPERVISOR -----")
        print(final_response)
        print("-----------------------------------------")
    else:
        print("No final response was generated.")
    print("\n\n----- FINAL RESPONSE -----\n")
    print(final_response)
    print("\n--------------------------\n")

    return steps


if __name__ == "__main__":
    # When run directly, execute the demo and print detailed output
    print("Running AI Crew Chat Demonstration...")
    steps = demo_ai_crew_chat_workflow()
    
    # Print summary of agent interactions
    agent_sequence = []
    for step in steps:
        if "next" in step:
            agent_sequence.append(step["next"])
    
    print("\nAgent Interaction Sequence:")
    print(" -> ".join(agent_sequence))
