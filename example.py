from langchain_openai import ChatOpenAI
from app.core.agents import create_agent, create_supervisor
from app.core.graph import AgentGraph, AgentState
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv
import os

load_dotenv()

# Set up the models
llm = ChatOpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
    model="google/gemini-2.5-flash",
)

# Define a simple tool
@tool
def simple_tool(query: str) -> str:
    """A simple tool that returns a fixed string."""
    return "This is a simple tool."

# Create the agents
agent1 = create_agent(llm, [simple_tool], "You are agent 1.")
agent2 = create_agent(llm, [], "You are agent 2.")

agents = [
    {"name": "agent1", "agent": agent1},
    {"name": "agent2", "agent": agent2},
]

# Create the supervisor
supervisor = create_supervisor(
    llm,
    agents,
    "You are the supervisor. Your job is to route the conversation to the correct agent.",
)

# Create the graph
graph = AgentGraph(supervisor, agents)

# Compile the graph
app = graph.compile()

# Run the graph
for s in app.stream(
    {
        "messages": [
            HumanMessage(content="What is the weather in San Francisco?")
        ]
    }
):
    if "__end__" not in s:
        print(s)
        print("----")
