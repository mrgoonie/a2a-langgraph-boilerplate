from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated, Sequence, List, Dict, Any, Callable
import operator
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_core.runnables import RunnableLambda
from langgraph.prebuilt import ToolNode, tools_condition
from app.core.logging import get_logger

logger = get_logger(__name__)

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    next: str
    # Optional context tracking
    context_summary: str
    message_count: int

def log_tools_condition(state):
    logger.info(f"Tools condition state: {state}")
    return tools_condition(state)


def summarize_messages(messages: List[BaseMessage], max_keep: int = 3) -> List[BaseMessage]:
    """
    Summarize message history to reduce token consumption.
    
    Args:
        messages: The list of messages to summarize
        max_keep: Maximum number of recent messages to keep in full
        
    Returns:
        A reduced list of messages with historical context summarized
    """
    if len(messages) <= max_keep:
        return messages
    
    # Keep the first message (usually the user query) and the last max_keep messages
    keep_messages = [messages[0]] + messages[-max_keep:]
    
    # Create a summary of the dropped messages
    dropped_messages = messages[1:-max_keep]
    if dropped_messages:
        summary_content = f"Summary of {len(dropped_messages)} previous messages: "
        summary_content += "Agents discussed the query and exchanged information about machine learning concepts."
        
        # Insert the summary message between the first message and recent messages
        keep_messages.insert(1, SystemMessage(content=summary_content))
    
    return keep_messages


def manage_context_growth(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Manage context growth to prevent token limit issues.
    This function processes the state before passing it to any agent.
    """
    # Initialize tracking variables if they don't exist
    if "message_count" not in state:
        state["message_count"] = 0
    
    if "messages" in state:
        # Track message count
        state["message_count"] = len(state["messages"])
        
        # Apply summarization when message count exceeds threshold
        if state["message_count"] > 5:
            logger.info(f"Summarizing {len(state['messages'])} messages to reduce context size")
            state["messages"] = summarize_messages(state["messages"])
            logger.info(f"Context reduced to {len(state['messages'])} messages")
            
            # Update count after summarization
            state["message_count"] = len(state["messages"])
    
    return state


class ContextManager:
    """Wrapper class to manage context growth in the agent graph"""
    
    def __call__(self, state):
        """Process the state to manage context growth"""
        return manage_context_growth(state)

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
                {"tools": "tools", "continue": agent["name"], "__end__": END},
            )
            self.workflow.add_edge(agent["name"], "supervisor")

        def supervisor_router(x):
            logger.info(f"Supervisor state: {x}")
            # Check if we're reaching termination conditions
            if "next" in x and (x["next"] == "FINISH" or x["next"] == "__end__"):
                logger.info(f"Supervisor signaling termination with: {x['next']}")
                return x["next"]
            
            # Check for recursion depth to force termination if needed
            if "messages" in x and len(x["messages"]) > 8: # Force termination after certain message depth
                logger.info("Forcing workflow termination due to message depth limit")
                return "FINISH"
            
            # Normal routing
            return x["next"] if "next" in x else "FINISH" # Default to FINISH if next is missing

        # Add all possible routing destinations including immediate termination
        self.workflow.add_conditional_edges(
            "supervisor",
            supervisor_router,
            {agent["name"]: agent["name"] for agent in self.agents} | 
            {"FINISH": END, "__end__": END, None: END} # Handle all possible termination signals
        )
        
        # Create a context manager node that will handle message summarization
        context_manager = ContextManager()
        
        # Add the context manager as a node to process state before the supervisor
        self.workflow.add_node("pre_process", RunnableLambda(context_manager))
        
        # Add the context manager to the start of the workflow
        self.workflow.set_entry_point("pre_process")
        
        # Connect pre_process to supervisor
        self.workflow.add_edge("pre_process", "supervisor")
        
        # Tool node connection
        self.workflow.add_edge("tools", "pre_process")


    def compile(self, **kwargs):
        """Compile the agent graph with optional configuration parameters.
        
        Args:
            **kwargs: Additional parameters to pass to the workflow compiler,
                     such as recursion_limit to control maximum graph iterations.
                     
        Returns:
            The compiled workflow graph ready for execution.
        """
        logger.info(f"Compiling graph with options: {kwargs}")
        return self.workflow.compile(**kwargs)
