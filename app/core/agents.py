from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain.output_parsers.openai_tools import JsonOutputToolsParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableLambda
from typing import List, Dict, Any

def create_agent(llm: ChatOpenAI, tools: list, system_prompt: str, name: str):
    """Creates a named agent executor that returns messages."""
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="messages"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ]
    )
    agent = create_tool_calling_agent(llm, tools, prompt)
    executor = AgentExecutor(agent=agent, tools=tools, handle_parsing_errors=True)

    def _agent_invoker(state):
        """Invokes the agent executor and formats the output as a message."""
        result = executor.invoke(state)
        
        # The output from an agent executor is a dict with an 'output' key.
        # We convert this to an AIMessage with the correct name.
        output_message = AIMessage(
            content=str(result["output"]), 
            name=name,
            # Pass tool calls if they exist
            tool_calls=result.get("tool_calls", [])
        )
        
        return {"messages": [output_message]}

    return RunnableLambda(_agent_invoker)

def create_supervisor(llm: ChatOpenAI, agents: List[Dict[str, Any]], system_prompt: str):
    options = [agent["name"] for agent in agents] + ["FINISH"]
    
    function_def = {
        "name": "route",
        "description": "Select the next agent to act. Or FINISH if the task is complete.",
        "parameters": {
            "title": "routeSchema",
            "type": "object",
            "properties": {
                "next": {
                    "title": "Next",
                    "anyOf": [
                        {"enum": options},
                    ],
                },
                "reasoning": {
                    "title": "Reasoning",
                    "type": "string",
                    "description": "Your reasoning and response to the user"
                }
            },
            "required": ["next", "reasoning"],
        },
    }
    
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="messages"),
            (
                "system",
                "Given the conversation above, provide your reasoning/response and then decide who should act next."
                " Or should we FINISH? Select one of: {options}",
            ),
        ]
    ).partial(options=str(options), agent_names=", ".join([agent["name"] for agent in agents]))

    def _supervisor_invoker(state):
        """Invokes the supervisor and formats the output as both a message and routing decision."""
        # Get the structured output from the LLM
        result = (prompt | llm.with_structured_output(function_def)).invoke(state)
        
        # Add the supervisor's reasoning as an AIMessage to the conversation
        supervisor_message = AIMessage(
            content=result.get("reasoning", "Processing request..."),
            name="supervisor"
        )
        
        # Return both the message and the routing decision
        return {
            "messages": [supervisor_message],
            "next": result["next"]
        }
    
    return RunnableLambda(_supervisor_invoker)

def create_final_response_chain(llm: ChatOpenAI):
    """Creates a chain to generate the final response from the conversation history."""
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful AI assistant. Synthesize the conversation history and provide a final, comprehensive answer to the user's initial request. The user's initial request was: {initial_request}"),
        MessagesPlaceholder(variable_name="messages")
    ])
    
    chain = (
        {
            "messages": lambda x: x["messages"],
            "initial_request": lambda x: x["messages"][0].content
        }
        | prompt
        | llm
    )
    return chain
