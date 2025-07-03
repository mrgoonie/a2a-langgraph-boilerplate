import os
import asyncio
from contextlib import AsyncExitStack
from langgraph.prebuilt import ToolNode
from langchain_core.tools import tool
from langchain_mcp_adapters.client import MultiServerMCPClient
# Keep imports below for backward compatibility if needed
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client


def create_tool_node(tools: list):
    return ToolNode(tools)

def create_search_api_tool():
    # Use the MCP server tools instead of direct Tavily integration
    # This will be populated with actual MCP tools during workflow execution
    # The search tool will be available via the MCP server at runtime
    return []  # Empty list as the tools will be obtained from MCP server

async def async_create_mcp_tools(mcp_server_url: str):
    """Create MCP tools by connecting to the server via Streamable HTTP transport using langchain-mcp-adapters.
    
    This function dynamically fetches available tools from the MCP server at runtime,
    using the MultiServerMCPClient from langchain-mcp-adapters which handles session ID issues
    that occur with direct MCP client usage.
    
    Args:
        mcp_server_url: The URL of the MCP server to connect to
        
    Returns:
        A list of tools available from the MCP server
    """
    print(f"DEBUG: Connecting to MCP server: {mcp_server_url}")
    
    try:
        print("DEBUG: Setting up MultiServerMCPClient")
        # Setup connection configuration for the MultiServerMCPClient
        # Using a server name of 'default' for simplicity
        connections = {
            "default": {
                "url": mcp_server_url,
                "transport": "streamable_http",
                # No authentication headers needed for SearchAPI MCP server
                "headers": {}
            }
        }
        
        # Create the MultiServerMCPClient with our connection config
        print("DEBUG: Creating MultiServerMCPClient")
        client = MultiServerMCPClient(connections=connections)
        
        # Fetch all available tools from the MCP server
        print("DEBUG: Fetching available tools")
        tools = await client.get_tools()
        print(f"DEBUG: Successfully connected to MCP server and retrieved {len(tools) if tools else 0} tools")
        
        # Print details about the tools for debugging
        if tools:
            for i, tool in enumerate(tools):
                print(f"DEBUG: Tool {i+1} - Name: {tool.name}")
                print(f"DEBUG: Tool {i+1} - Description: {tool.description[:50]}..." if len(tool.description) > 50 else tool.description)
        
        return tools
    except Exception as e:
        print(f"ERROR: Failed connecting to MCP server: {str(e)}")
        import traceback
        print("DEBUG: Exception traceback:")
        traceback.print_exc()
        # Return empty list to allow the workflow to continue
        return []

def create_mcp_tools(mcp_server_url: str):
    return asyncio.run(async_create_mcp_tools(mcp_server_url))
