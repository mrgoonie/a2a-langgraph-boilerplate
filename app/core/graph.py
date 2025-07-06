from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated, Sequence, List, Dict, Any, Callable, Literal, Union
import operator
import copy
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_core.runnables import RunnableLambda
from langgraph.prebuilt import ToolNode
from langgraph.types import Command, Send
from app.core.logging import get_logger
from app.core.agents import create_final_response_chain

logger = get_logger(__name__)

class StateManager:
    """
    Global state manager that ensures state persistence across LangGraph nodes in an edgeless graph.
    
    This solves a critical issue with LangGraph's Command objects potentially not preserving all state 
    attributes between node transitions, which can cause visit counters and other important state to reset.
    
    The StateManager maintains a global state dictionary that is preserved across all node transitions,
    ensuring that even when using the Command/Send API, stateful information like visit counters 
    remains consistent. This is essential for implementing termination conditions and preventing
    infinite loops in edgeless LangGraph workflows.
    
    Usage:
        1. Initialize with initial state via StateManager.init_state(initial_state)
        2. In each node wrapper, use StateManager.ensure_counters(state) to preserve counters
        3. After processing, use StateManager.update_state(updated_state) to update global state
        4. When creating Command objects, use StateManager.create_command(state, goto) instead of
           directly using Command constructor to ensure all state is properly propagated
    """
    _global_state = {}
    
    @classmethod
    def init_state(cls, state):
        """Initialize the global state from the initial state"""
        cls._global_state = copy.deepcopy(state)
    
    @classmethod
    def update_state(cls, state):
        """Update the global state with values from the provided state"""
        if isinstance(state, dict):
            # For new values, add them to global state
            for key, value in state.items():
                cls._global_state[key] = copy.deepcopy(value)
        return cls._global_state
    
    @classmethod
    def get_state(cls):
        """Get the current global state"""
        return copy.deepcopy(cls._global_state)
    
    @classmethod
    def ensure_counters(cls, state):
        """Ensure visit counters exist in the state"""
        result_state = copy.deepcopy(state)
        
        # Initialize or copy supervisor_visits counter
        if "supervisor_visits" not in result_state and "supervisor_visits" in cls._global_state:
            result_state["supervisor_visits"] = cls._global_state["supervisor_visits"]
        elif "supervisor_visits" not in result_state:
            result_state["supervisor_visits"] = 0
            
        # Initialize or copy agent_visits counter
        if "agent_visits" not in result_state and "agent_visits" in cls._global_state:
            result_state["agent_visits"] = copy.deepcopy(cls._global_state["agent_visits"])
        elif "agent_visits" not in result_state:
            result_state["agent_visits"] = {}
            
        return result_state
    
    @classmethod
    def create_command(cls, state, goto):
        """Create a Command object with the merged state"""
        # Update the global state with the current state
        cls.update_state(state)
        
        # Return a command with the complete global state
        return Command(update=cls.get_state(), goto=goto)


class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    next: str
    # Optional context tracking
    context_summary: str
    message_count: int

# Tools condition helper function that returns a Command to route to the appropriate node
def tools_condition_command(state):
    logger.info(f"Tools condition state: {state}")
    result = {"tools": "tools", "continue": None, "__end__": END}
    tool_calls = state.get("messages", [])[-1].tool_calls
    
    if not tool_calls:
        # No tool calls, continue with the current agent
        return Command(goto="continue")
    else:
        # Tool calls present, route to tools
        return Command(goto="tools")


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
    def __init__(self, supervisor, agents, tools, supervisor_llm):
        self.supervisor = supervisor
        self.supervisor_llm = supervisor_llm
        self.agents = agents
        self.workflow = StateGraph(AgentState)
        
        # Supervisor wrapper function that returns Command objects
        def wrap_supervisor(state: AgentState) -> Command:
            # First run - initialize global state
            if not StateManager._global_state:
                StateManager.init_state(state)
                
            # Ensure state has all required counters
            state = StateManager.ensure_counters(state)
            
            # Debug: Log incoming state
            logger.info(f"SUPERVISOR ENTRY - supervisor_visits={state.get('supervisor_visits', 0)}, "  
                      f"agent_visits={state.get('agent_visits', {})}")
            
            # Apply the original supervisor function to get the updated state
            # Must use invoke() method because supervisor is a RunnableSequence, not a callable function
            updated_state = self.supervisor.invoke(state)
            
            # Update global state
            StateManager.update_state(updated_state)
            
            # Determine where to go next
            if "next" in updated_state and (updated_state["next"] == "FINISH" or updated_state["next"] == "__end__"):
                logger.info(f"Supervisor signaling termination with: {updated_state['next']}")
                
                # Check if any agents have been visited
                agent_visits = StateManager.get_state().get('agent_visits', {})
                if not agent_visits or all(v == 0 for v in agent_visits.values()):
                    # If no agents were involved, the supervisor's message is already in the state
                    logger.info("No agents involved. Supervisor's response is already in messages.")
                else:
                    # If agents were involved, generate a synthesized final response
                    logger.info("Generating final synthesized response from supervisor.")
                    final_response_chain = create_final_response_chain(self.supervisor_llm)
                    final_response_obj = final_response_chain.invoke(updated_state)
                    final_message = AIMessage(
                        content=final_response_obj.content,
                        name="supervisor"
                    )
                    updated_state["messages"].append(final_message)
                
                # 4. Update the global state before terminating
                StateManager.update_state(updated_state)
                
                return StateManager.create_command(updated_state, END)
            
            # Check for explicit completion message from supervisor
            last_message = updated_state.get("messages", [])[-1] if updated_state.get("messages", []) else None
            if last_message and hasattr(last_message, "content") and isinstance(last_message.content, str):
                if "FINAL RESPONSE:" in last_message.content or "TASK COMPLETED" in last_message.content:
                    logger.info(f"Detected completion message in supervisor output, terminating workflow")
                    return StateManager.create_command(updated_state, END)
            
            # Force termination after a certain number of supervisor visits 
            global_state = StateManager.get_state()
            supervisor_visits = global_state.get("supervisor_visits", 0) + 1
            
            # Update the supervisor visit count in both global state and local state
            StateManager.update_state({"supervisor_visits": supervisor_visits})
            updated_state["supervisor_visits"] = supervisor_visits
            
            # Ensure agent_visits is properly preserved
            if "agent_visits" in global_state:
                updated_state["agent_visits"] = copy.deepcopy(global_state["agent_visits"])
                
            logger.info(f"After supervisor update: global state agent_visits = {StateManager.get_state().get('agent_visits', {})}")
            logger.info(f"After supervisor update: local state agent_visits = {updated_state.get('agent_visits', {})}")
            
            
            # Debug: Log updated supervisor visit count
            logger.info(f"SUPERVISOR VISIT COUNT: {supervisor_visits}/{5} (before termination check)")
            
            if supervisor_visits > 5:
                logger.info(f"CRITICAL: Forcing termination after {supervisor_visits} supervisor visits")
                return StateManager.create_command(updated_state, END)
            
            # Check for recursion depth to force termination based on message count
            if "message_count" in updated_state and updated_state["message_count"] > 6:
                logger.info(f"Forcing workflow termination due to message count limit: {updated_state['message_count']}")
                return StateManager.create_command(updated_state, END)
            
            # Check for recursion depth to force termination based on message list length
            if "messages" in updated_state and len(updated_state["messages"]) > 12:
                logger.info(f"Forcing workflow termination due to message depth limit: {len(updated_state['messages'])})")
                return StateManager.create_command(updated_state, END)
            
            # Normal routing - get the next agent from the state
            if "next" in updated_state and updated_state["next"] in [agent["name"] for agent in self.agents]:
                next_agent = updated_state["next"]
                logger.info(f"Routing to agent: {next_agent}")
                return StateManager.create_command(updated_state, next_agent)
            
            # Default to END if next is missing or invalid
            logger.info("No valid next agent specified, terminating workflow")
            return StateManager.create_command(updated_state, END)
        
        # Create wrapper functions for each agent to return Command objects
        def create_agent_wrapper(agent_node, agent_name):
            def wrapped_agent(state: AgentState):
                # Ensure state has all required counters
                state = StateManager.ensure_counters(state)
                
                # Debug: Log incoming state
                logger.info(f"AGENT {agent_name} ENTRY - agent_visits={state.get('agent_visits', {}).get(agent_name, 0)}, "
                          f"supervisor_visits={state.get('supervisor_visits', 0)}")
                
                # Get the current agent visit counters from global state
                global_state = StateManager.get_state()
                
                # Ensure agent_visits exists in the global state
                if "agent_visits" not in global_state:
                    global_state["agent_visits"] = {}
                    
                # Create a deep copy to avoid reference issues
                agent_visits = copy.deepcopy(global_state.get("agent_visits", {}))
                
                # Increment the visit counter for this specific agent
                agent_visits[agent_name] = agent_visits.get(agent_name, 0) + 1
                
                # Update the global state with the new visit count
                logger.info(f"Updating agent_visits counter for {agent_name}: {agent_visits[agent_name]}")
                StateManager.update_state({"agent_visits": agent_visits})
                
                # Double check that the update was successful
                logger.info(f"After update: global state agent_visits = {StateManager.get_state().get('agent_visits', {})}")
                
                # Force copy the visit counter to the current state object
                state["agent_visits"] = copy.deepcopy(agent_visits)
                
                # Debug: Log updated agent visit count
                logger.info(f"AGENT {agent_name} VISIT COUNT: {agent_visits[agent_name]}/3 (before termination check)")
                
                # Enforce termination if agent has been visited too many times
                if agent_visits.get(agent_name, 0) >= 3:  # Lower threshold to ensure termination
                    logger.info(f"CRITICAL: Forcing termination: agent {agent_name} has been visited {agent_visits[agent_name]} times")
                    # Create a new state dict with termination info
                    updated_state = state.copy() if isinstance(state, dict) else dict(state)
                    updated_state["termination_reason"] = f"Max visits to {agent_name} reached"
                    # Add a summary message to indicate forced termination
                    if "messages" in updated_state:
                        content = f"[SYSTEM] Workflow terminated due to max visits ({agent_visits[agent_name]}) to {agent_name}."
                        updated_state["messages"].append({"type": "system", "content": content})
                    # Ensure the termination is logged and propagated
                    logger.info(f"TERMINATING WORKFLOW: Max visits to {agent_name} reached")
                    return StateManager.create_command(updated_state, END)
                
                # Apply the original agent function to get the updated state
                # Must use invoke() method because agent_node is a RunnableSequence, not a callable function
                updated_state = agent_node.invoke(state)

                # Manually name the agent's response message
                if updated_state.get("messages"):
                    last_message = updated_state["messages"][-1]
                    if isinstance(last_message, AIMessage):
                        # Create a copy and set the name to avoid mutation issues
                        new_message = last_message.model_copy() if hasattr(last_message, 'model_copy') else last_message.copy()
                        new_message.name = agent_name
                        updated_state["messages"][-1] = new_message
                
                # Update the global state with the agent's results
                StateManager.update_state(updated_state)
                
                # Debug: Log agent state after processing
                logger.info(f"AGENT {agent_name} EXIT - agent_visits after processing={StateManager.get_state().get('agent_visits', {})}")
                
                # Check if the last message has tool calls
                last_message = updated_state.get("messages", [])[-1] if updated_state.get("messages", []) else None
                tool_calls = getattr(last_message, "tool_calls", None) if last_message else None
                
                if tool_calls:
                    # If there are tool calls, route to the tools node
                    logger.info(f"Agent {agent_name} is calling tools")
                    return StateManager.create_command(updated_state, "tools")
                else:
                    # Otherwise, route back to supervisor
                    logger.info(f"Agent {agent_name} is routing to supervisor")
                    return StateManager.create_command(updated_state, "supervisor")
            
            return wrapped_agent
        
        # Add tools node
        self.workflow.add_node("tools", ToolNode(tools))
        
        # Add pre-process context manager node
        context_manager = ContextManager()
        self.workflow.add_node("pre_process", RunnableLambda(context_manager))
        
        # Set the entry point
        self.workflow.set_entry_point("pre_process")
        
        # Add supervisor node with wrapped function
        self.workflow.add_node("supervisor", wrap_supervisor)
        
        # Connect pre_process to supervisor
        self.workflow.add_edge("pre_process", "supervisor")
        
        # Add agent nodes with wrapped functions
        for agent in self.agents:
            wrapped_agent = create_agent_wrapper(agent["agent"], agent["name"])
            self.workflow.add_node(agent["name"], wrapped_agent)
        
        # Add edge from tools back to pre_process
        self.workflow.add_edge("tools", "pre_process")


    def compile(self, **kwargs):
        """Compile the agent graph with optional configuration parameters.
        
        Args:
            **kwargs: Additional parameters to pass to the workflow compiler.
                     Note: recursion_limit should NOT be passed here; use the
                     with_config() method on the compiled graph or pass
                     config={'recursion_limit': N} when invoking.
                     
        Returns:
            The compiled workflow graph ready for execution.
        """
        logger.info(f"Compiling graph with options: {kwargs}")
        # Filter out recursion_limit if present, as it's not supported in StateGraph.compile()
        if 'recursion_limit' in kwargs:
            recursion_limit = kwargs.pop('recursion_limit')
            logger.info(f"Removed recursion_limit={recursion_limit} from compile options; it should be used with .with_config() instead")
            
        graph = self.workflow.compile(**kwargs)
        
        # If recursion_limit was specified, apply it to the compiled graph
        if 'recursion_limit' in locals():
            logger.info(f"Applying recursion_limit={recursion_limit} to compiled graph")
            graph = graph.with_config(recursion_limit=recursion_limit)
            
        return graph
