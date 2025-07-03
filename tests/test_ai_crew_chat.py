import os
import sys
import random
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.language_models import FakeListChatModel
from langchain_core.tools import tool

# Add the project root to the path so we can import the app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.agents import create_agent, create_supervisor
from app.core.graph import AgentGraph

# Load environment variables
load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env'))

# No need to check for API key when using mock LLM
print("Using mock LLM for demonstration purposes")

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
    # Use a fake LLM with predefined responses to demonstrate the workflow
    print("Setting up mock LLM for demonstration...")
    
    # Define mock responses for different agents as strings (not AIMessage objects)
    researcher_responses = [
        "I've researched machine learning algorithms and found that decision trees are a fundamental supervised learning method."
    ]
    
    coder_responses = [
        "Here's a simple Python example of a decision tree classifier:\n\n```python\nfrom sklearn.tree import DecisionTreeClassifier\nimport numpy as np\n\n# Sample data\nX = np.array([[0, 0], [1, 1], [0, 1], [1, 0]])\ny = np.array([0, 0, 1, 1])\n\n# Train model\nclf = DecisionTreeClassifier()\nclf.fit(X, y)\n\n# Make predictions\npredictions = clf.predict(X)\nprint(f'Predictions: {predictions}')\n```"
    ]
    
    summarizer_responses = [
        "Decision trees work by splitting data based on feature values to create a tree-like structure of decisions. Each internal node represents a test on a feature, each branch represents the outcome of that test, and each leaf node represents a class label. They're intuitive and easy to visualize, making them great for beginners to understand."
    ]
    
    # Create different LLMs for different agents
    researcher_llm = FakeListChatModel(responses=researcher_responses)
    coder_llm = FakeListChatModel(responses=coder_responses)
    summarizer_llm = FakeListChatModel(responses=summarizer_responses)
    
    # For the supervisor, create responses that delegate tasks and synthesize results
    supervisor_responses = [
        "I'll delegate this task to our researcher to learn about ML algorithms first.",
        "Now I'll ask our coder to provide a Python example of decision trees.",
        "Finally, I'll have our summarizer create a simple explanation of decision trees.",
        "Here's a comprehensive response to your query:\n\n**Research on ML Algorithms:**\nDecision trees are a fundamental supervised learning method in machine learning.\n\n**Python Example:**\n```python\nfrom sklearn.tree import DecisionTreeClassifier\nimport numpy as np\n\n# Sample data\nX = np.array([[0, 0], [1, 1], [0, 1], [1, 0]])\ny = np.array([0, 0, 1, 1])\n\n# Train model\nclf = DecisionTreeClassifier()\nclf.fit(X, y)\n\n# Make predictions\npredictions = clf.predict(X)\nprint(f'Predictions: {predictions}')\n```\n\n**Simple Explanation:**\nDecision trees work by splitting data based on feature values to create a tree-like structure of decisions. Each internal node represents a test on a feature, each branch represents the outcome of that test, and each leaf node represents a class label. They're intuitive and easy to visualize."
    ]
    
    supervisor_llm = FakeListChatModel(responses=supervisor_responses)
    
    # Use supervisor_llm as the main LLM for demonstration
    llm = supervisor_llm
    
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
