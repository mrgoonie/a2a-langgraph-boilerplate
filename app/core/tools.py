import asyncio
from contextlib import AsyncExitStack
from langgraph.prebuilt import ToolNode
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.tools import tool
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client


def create_tool_node(tools: list):
    return ToolNode(tools)

def create_tavily_tool():
    return TavilySearchResults(max_results=1)

async def async_create_mcp_tools(mcp_server_url: str):
    async with AsyncExitStack() as stack:
        read, write, get_session_id = await stack.enter_async_context(
            streamablehttp_client(url=mcp_server_url)
        )
        session = ClientSession(read, write)
        await session.initialize()
        tools = await session.list_tools()
        return tools

def create_mcp_tools(mcp_server_url: str):
    return asyncio.run(async_create_mcp_tools(mcp_server_url))
