from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated, Sequence
import operator
from langchain_core.messages import BaseMessage
from langgraph.prebuilt import ToolNode, tools_condition
from app.core.logging import get_logger

logger = get_logger(__name__)

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    next: str

def log_tools_condition(state):
    logger.info(f"Tools condition state: {state}")
    return tools_condition(state)

class AgentGraph:
    def __init__(self, supervisor, agents, tools):
        self.supervisor = supervisor
        self.agents = agents
        self.workflow = StateGraph(AgentState)
        self.workflow.add_node("supervisor", self.supervisor)
        self.workflow.add_node("tools", ToolNode(tools))

        for agent in self.agents:
            self.workflow.add_node(agent["name"], agent["agent"])
            self.workflow.add_conditional_edges(
                agent["name"],
                log_tools_condition,
                {"tools": "tools", "continue": agent["name"]},
            )
            self.workflow.add_edge(agent["name"], "supervisor")

        def supervisor_router(x):
            logger.info(f"Supervisor state: {x}")
            return x["next"]

        self.workflow.add_conditional_edges(
            "supervisor",
            supervisor_router,
            {agent["name"]: agent["name"] for agent in self.agents} | {"FINISH": END}
        )
        self.workflow.add_edge("tools", "supervisor")
        self.workflow.set_entry_point("supervisor")


    def compile(self):
        return self.workflow.compile()
