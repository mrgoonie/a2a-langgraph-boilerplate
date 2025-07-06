from sqlalchemy.orm import Session
from uuid import UUID
import asyncio
import time
from app.models.crew import Crew
from app.models.agent import Agent
from app.models.mcp_server import McpServer
from app.schemas.crew import CrewCreate
from app.schemas.prompt import PromptCreate
from app.core.agents import create_agent, create_supervisor
from app.core.graph import AgentGraph
from app.core.tools import create_search_api_tool, async_create_mcp_tools
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableConfig
from app.core.logging import get_logger
from langchain_mcp_adapters.client import MultiServerMCPClient
from dotenv import load_dotenv
import os

logger = get_logger(__name__)

load_dotenv()

llm = ChatOpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
    model="google/gemini-2.5-flash",
)

def create_crew(db: Session, crew: CrewCreate):
    # Create the crew instance
    db_crew = Crew(name=crew.name)
    db.add(db_crew)
    db.commit() # Commit to get the crew ID

    # Create the default supervisor agent for this crew
    supervisor_agent = Agent(
        name="supervisor",
        role="supervisor",
        system_prompt="You are a supervisor. Your job is to manage a team of agents to solve the user's request.",
        crew_id=db_crew.id
    )
    db.add(supervisor_agent)
    db.commit()
    db.refresh(db_crew)

    return db_crew

def get_crew(db: Session, crew_id: UUID):
    return db.query(Crew).filter(Crew.id == crew_id).first()

def get_crews(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Crew).offset(skip).limit(limit).all()

def update_crew(db: Session, crew_id: UUID, crew: CrewCreate):
    db_crew = db.query(Crew).filter(Crew.id == crew_id).first()
    if db_crew is None:
        return None
    
    db_crew.name = crew.name
    db.commit()
    db.refresh(db_crew)
    return db_crew

def delete_crew(db: Session, crew_id: UUID):
    db_crew = db.query(Crew).filter(Crew.id == crew_id).first()
    if db_crew is None:
        return None
        
    db.delete(db_crew)
    db.commit()
    return db_crew

async def _execute_prompt_async(db: Session, crew_id: UUID, prompt: PromptCreate):
    """Internal async implementation of execute_prompt for async tool handling.
    
    This async function handles all operations that require async support,
    including MCP tool fetching and workflow execution.
    """
    # Internal implementation starts without duplicate logging
    start_time = time.time()
    crew = get_crew(db, crew_id)
    if not crew:
        logger.error(f"Crew not found with ID: {crew_id}")
        return {"error": "Crew not found"}
    
    logger.info(f"Found crew: {crew.name} with {len(crew.agents)} agents")
    try:
        supervisor_model = db.query(Agent).filter(Agent.crew_id == crew_id, Agent.role == "supervisor").first()
        if not supervisor_model:
            logger.error(f"Supervisor not found for crew: {crew.name}")
            return {"error": "Supervisor not found for this crew"}
        
        logger.info(f"Found supervisor agent: {supervisor_model.name}")

        logger.info("Initializing agent tools")
        agents_data = []
        tools = create_search_api_tool()  # Empty list as tools will come from MCP
        
        # Dynamically get all available MCP servers from database
        logger.info("Fetching all MCP servers from database")
        mcp_servers = db.query(McpServer).all()
        
        if mcp_servers:
            # Create a dynamic connection config for MultiServerMCPClient
            connections = {}
            logger.info(f"Found {len(mcp_servers)} MCP servers in database")
            
            # Add each MCP server to the connections dictionary
            for mcp_server in mcp_servers:
                logger.info(f"Adding MCP server: {mcp_server.name} ({mcp_server.url})")
                connections[mcp_server.name] = {
                    "url": mcp_server.url,
                    "transport": "streamable_http",
                    # No authentication headers by default
                    "headers": {}
                }
            
            try:
                # Create resilient MCP tools using our custom wrapper
                logger.info("Creating resilient MCP tools")
                tool_start_time = time.time()
                
                # Instead of using MultiServerMCPClient directly, use our async_create_mcp_tools function
                # which creates resilient MCP tools with retry and error handling
                mcp_tools = []
                for mcp_server in mcp_servers:
                    # Create resilient MCP tools with 3 retries max
                    server_tools = await async_create_mcp_tools(
                        mcp_server_url=mcp_server.url,
                        use_resilient_wrapper=True,  # Enable our resilient wrapper
                        max_retries=3  # Set max retries to 3 for better reliability
                    )
                    if server_tools:
                        mcp_tools.extend(server_tools)
                        logger.info(f"Added {len(server_tools)} resilient tools from {mcp_server.name}")
                
                tool_elapsed = time.time() - tool_start_time
                logger.info(f"Resilient MCP tool creation took {tool_elapsed:.2f} seconds")
                
                if mcp_tools:
                    tools.extend(mcp_tools)
                    logger.info(f"Added {len(mcp_tools)} MCP tools to agent toolset")
                    for i, tool in enumerate(mcp_tools):
                        logger.info(f"  Tool {i+1}: {tool.name} - {tool.description[:50]}...")
            except Exception as e:
                logger.error(f"Error getting MCP tools: {str(e)}")
                logger.warning("Continuing without MCP tools due to error - agents will have limited capabilities")
                import traceback
                logger.debug(traceback.format_exc())
        
        logger.info("Creating agents for crew")
        for agent_model in crew.agents:
            if agent_model.role != "supervisor":
                logger.info(f"Creating agent: {agent_model.name} with role: {agent_model.role}")
                # Create agent-specific LLM instance if model is specified
                agent_llm = llm
                if agent_model.model:
                    logger.info(f"Using custom model for agent {agent_model.name}: {agent_model.model}")
                    agent_llm = ChatOpenAI(
                        base_url="https://openrouter.ai/api/v1",
                        api_key=os.getenv("OPENROUTER_API_KEY"),
                        model=agent_model.model,
                    )
                agent = create_agent(agent_llm, tools, agent_model.system_prompt, agent_model.name)
                agents_data.append({"name": agent_model.name, "agent": agent})
                logger.info(f"Added agent {agent_model.name} to crew")

        logger.info("Creating supervisor agent")
        # Create supervisor-specific LLM instance if model is specified
        supervisor_llm = llm
        if supervisor_model.model:
            logger.info(f"Using custom model for supervisor {supervisor_model.name}: {supervisor_model.model}")
            supervisor_llm = ChatOpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=os.getenv("OPENROUTER_API_KEY"),
                model=supervisor_model.model,
            )
        supervisor = create_supervisor(
            supervisor_llm,
            agents_data,
            supervisor_model.system_prompt,
        )
        logger.info("Supervisor agent created successfully")

        logger.info("Creating agent graph")
        graph_start_time = time.time()
        graph = AgentGraph(supervisor=supervisor, agents=agents_data, tools=tools, supervisor_llm=supervisor_llm)
        # Set a higher recursion limit to prevent premature termination
        app = graph.compile(recursion_limit=50)
        graph_elapsed = time.time() - graph_start_time
        logger.info(f"Agent graph compilation took {graph_elapsed:.2f} seconds")
        
        # Create a config that allows async tools to run properly
        logger.info("Creating runnable config for async execution")
        config = RunnableConfig(
            recursion_limit=25,  # Use lower limit to increase speed and reduce tokens
            configurable={
                "thread_pool_executor": None,  # Use asyncio executor
            }
        )
        
        # Process the user's prompt - we're already in an async context
        logger.info("Starting async workflow execution")
        exec_start_time = time.time()
        try:
            # Set a lower recursion limit for the graph execution
            # Use this instead of the larger one set during compile time
            # This ensures the workflow will terminate faster if no end condition is reached
            recursion_limit = 10
            logger.info(f"Invoking graph with recursion_limit={recursion_limit} to prevent infinite loops")
            
            # Update config with the recursion_limit
            if config is None:
                config = {}
            config["recursion_limit"] = recursion_limit
            
            # Create a single HumanMessage object to prevent duplication
            human_message = HumanMessage(content=prompt.prompt)
            logger.info(f"Created human message with content: {prompt.prompt[:50]}...")
            
            # Initialize state with input prompt and counters
            initial_state = {
                "messages": [human_message],
                "message_count": 1,
                "agent_visits": {},      # Initialize agent visits counter
                "supervisor_visits": 0,   # Initialize supervisor visits counter
                "visit_threshold": 3,     # Maximum visits per agent before termination
                "supervisor_threshold": 5 # Maximum supervisor visits before termination
            }
            
            # Initialize the StateManager with our initial state
            from app.core.graph import StateManager
            StateManager.init_state(initial_state)
            logger.info(f"Initial state has {len(initial_state['messages'])} messages")
            
            # Invoke the graph with the initial state and updated config
            logger.info(f"Executing graph with initial state and visit counters initialized")
            result = await app.ainvoke(initial_state, config=config)
            
            exec_elapsed = time.time() - exec_start_time
            logger.info(f"Async workflow execution completed in {exec_elapsed:.2f} seconds")
            total_elapsed = time.time() - start_time
            logger.info(f"Total execution time: {total_elapsed:.2f} seconds")
            
            # Check if we need to generate a final response
            if isinstance(result, dict) and "messages" in result and len(result["messages"]) > 0:
                # Log message count and types for debugging
                message_types = [type(m).__name__ if hasattr(m, "__name__") else m["type"] if isinstance(m, dict) and "type" in m else type(m).__name__ for m in result["messages"]]
                logger.info(f"Result contains {len(result['messages'])} messages of types: {message_types}")
                
                # Apply a more robust deduplication of messages
                logger.info("Starting message deduplication process")
                
                # First try - deduplicate based on content equality
                unique_messages = []
                seen_contents = {}
                
                # Process all messages and only keep the first occurrence of each unique content
                for i, msg in enumerate(result["messages"]):
                    # Extract content depending on message type
                    if isinstance(msg, dict) and "content" in msg:
                        content = msg["content"]
                        msg_type = msg.get("type", "Unknown")
                    elif hasattr(msg, "content"):
                        content = msg.content
                        msg_type = msg.__class__.__name__
                    else:
                        # If we can't extract content, keep the message as is
                        unique_messages.append(msg)
                        continue
                    
                    # Use content as key to detect duplicates
                    content_key = f"{msg_type}:{content}"
                    if content_key not in seen_contents:
                        seen_contents[content_key] = i
                        unique_messages.append(msg)
                
                initial_count = len(result["messages"])
                final_count = len(unique_messages)
                
                if initial_count != final_count:
                    logger.warning(f"Removed {initial_count - final_count} duplicate messages")
                    # Update the result with de-duplicated messages
                    result["messages"] = unique_messages
                    # Keep only one human message with the original prompt
                    human_messages = [m for m in unique_messages 
                                   if (isinstance(m, dict) and m.get("type") == "HumanMessage") or 
                                      (hasattr(m, "__class__") and m.__class__.__name__ == "HumanMessage")]
                    
                    if len(human_messages) > 1:
                        # If we still have multiple human messages, keep only the first one
                        first_human = human_messages[0]
                        result["messages"] = [m for m in result["messages"] 
                                          if not ((isinstance(m, dict) and m.get("type") == "HumanMessage") or 
                                               (hasattr(m, "__class__") and m.__class__.__name__ == "HumanMessage"))]
                        result["messages"].insert(0, first_human)
                        logger.info(f"Kept only the first human message, now have {len(result['messages'])} messages")
                else:
                    logger.info("No duplicate messages found")
                    
                # Update message count
                result["message_count"] = len(result["messages"])
                
                # Ensure there is a final response message that answers the original query
                # If the last message isn't from the supervisor or there's no appropriate final message,
                # add one based on the query and available information
            
            return result
        except Exception as e:
            exec_elapsed = time.time() - exec_start_time
            logger.error(f"Async workflow execution failed after {exec_elapsed:.2f} seconds: {str(e)}")
            # Log detailed error information to help diagnose the issue
            import traceback
            logger.error(f"Detailed error traceback:")
            logger.error(traceback.format_exc())
            # Return a more helpful error message instead of re-raising
            return {
                "error": f"Workflow execution failed: {str(e)}",
                "status": "error",
                "exec_time": exec_elapsed
            }
    except Exception as e:
        import traceback
        total_elapsed = time.time() - start_time
        logger.error(f"Error executing prompt after {total_elapsed:.2f} seconds with traceback:")
        logger.error(traceback.format_exc())
        return {"error": f"Error executing prompt: {str(e)}"}


def execute_prompt(db: Session, crew_id: UUID, prompt: PromptCreate):
    """Execute a prompt with the AI crew, handling both sync and async tools.
    
    This function has been updated to properly support async tool invocation from
    langchain-mcp-adapters, which is necessary for the MCP tools to work correctly.
    
    The execution includes detailed logging to help diagnose timeouts and bottlenecks.
    """
    logger.info(f"Starting execute_prompt for crew_id {crew_id} with prompt: {prompt.prompt[:50]}...")
    
    # Use asyncio.run to run the async implementation
    try:
        return asyncio.run(_execute_prompt_async(db, crew_id, prompt))
    except Exception as e:
        import traceback
        logger.error(f"Error in execute_prompt wrapper:")
        logger.error(traceback.format_exc())
        return {"error": f"Error executing prompt: {str(e)}"}

