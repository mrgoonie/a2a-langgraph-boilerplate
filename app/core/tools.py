import os
import asyncio
import time
import logging
from typing import Dict, List, Any, Optional, Union, Callable
from contextlib import AsyncExitStack
from functools import wraps

from langgraph.prebuilt import ToolNode
from langchain_core.tools import tool, BaseTool, StructuredTool
# Use direct Pydantic import instead of deprecated langchain_core.pydantic_v1
from pydantic import create_model
from langchain_mcp_adapters.client import MultiServerMCPClient
# Keep imports below for backward compatibility if needed
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client
import httpx

# Configure logging
logger = logging.getLogger(__name__)


def create_tool_node(tools: list):
    return ToolNode(tools)

def create_search_api_tool():
    # Use the MCP server tools instead of direct Tavily integration
    # This will be populated with actual MCP tools during workflow execution
    # The search tool will be available via the MCP server at runtime
    return []  # Empty list as the tools will be obtained from MCP server

class ResilientMcpTool(StructuredTool):
    """A resilient wrapper around MCP tools that handles connection errors gracefully.
    
    This class wraps the standard MCP tools to add:
    - Timeout handling
    - Retry logic for transient errors
    - Graceful error messages for failed tool calls
    
    It helps prevent UnboundLocalError and other exceptions that might crash the agent workflow
    when MCP servers experience issues.
    """
    
    def __init__(self, base_tool: BaseTool, max_retries: int = 2, retry_delay: float = 1.0):
        """Initialize the resilient MCP tool wrapper.
        
        Args:
            base_tool: The original MCP tool to wrap
            max_retries: Maximum number of retries on failure (default: 2)
            retry_delay: Delay between retries in seconds (default: 1.0)
        """
        self._base_tool = base_tool
        self.name = base_tool.name
        self.description = base_tool.description
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        
        # Get the schema from the base tool
        if hasattr(base_tool, "args_schema"):
            self.args_schema = base_tool.args_schema
        else:
            # Create a new schema model if needed
            self.args_schema = create_model(
                f"{self.name}Schema",
                **{k: (v.annotation, v.default) for k, v in base_tool.args.items()}
            )
        
        # Set up the function signature for the tool
        @wraps(base_tool._run)
        def _run(**kwargs):
            return self._resilient_run(**kwargs)
        
        @wraps(base_tool._arun)
        async def _arun(**kwargs):
            return await self._resilient_arun(**kwargs)
        
        self._run = _run
        self._arun = _arun
    
    def _resilient_run(self, **kwargs) -> str:
        """Execute the tool with resilience, retrying on failures."""
        for attempt in range(self.max_retries + 1):
            try:
                return self._base_tool._run(**kwargs)
            except Exception as e:
                if attempt < self.max_retries:
                    logger.warning(f"MCP tool {self.name} failed (attempt {attempt+1}/{self.max_retries+1}): {str(e)}")
                    time.sleep(self.retry_delay)
                else:
                    logger.error(f"MCP tool {self.name} failed after {self.max_retries+1} attempts: {str(e)}")
                    return f"Error: Tool call failed after {self.max_retries+1} attempts. The external service may be unavailable or experiencing issues. {str(e)}"
    
    async def _resilient_arun(self, **kwargs) -> str:
        """Execute the tool asynchronously with resilience, retrying on failures."""
        for attempt in range(self.max_retries + 1):
            try:
                return await self._base_tool._arun(**kwargs)
            except (httpx.HTTPStatusError, httpx.ConnectError, httpx.ReadTimeout) as e:
                error_msg = f"Network error with MCP server: {str(e)}"
                if attempt < self.max_retries:
                    logger.warning(f"MCP tool {self.name} network error (attempt {attempt+1}/{self.max_retries+1}): {error_msg}")
                    await asyncio.sleep(self.retry_delay)
                else:
                    logger.error(f"MCP tool {self.name} network error after {self.max_retries+1} attempts: {error_msg}")
                    return f"Error: MCP server connection failed. The service might be temporarily unavailable or experiencing high load. Details: {str(e)}"
            except UnboundLocalError as e:
                # Specific handling for the UnboundLocalError in langchain_mcp_adapters/tools.py
                if "call_tool_result" in str(e):
                    error_msg = "MCP server connection failed during tool execution"
                    logger.error(f"MCP tool {self.name} failed with UnboundLocalError: {str(e)}")
                    return f"Error: {error_msg}. The MCP server might be unavailable or experiencing timeout issues."
                raise
            except Exception as e:
                error_msg = f"MCP tool execution error: {str(e)}"
                if attempt < self.max_retries:
                    logger.warning(f"MCP tool {self.name} error (attempt {attempt+1}/{self.max_retries+1}): {error_msg}")
                    await asyncio.sleep(self.retry_delay)
                else:
                    logger.error(f"MCP tool {self.name} error after {self.max_retries+1} attempts: {error_msg}")
                    return f"Error: Tool execution failed. Details: {str(e)}"


async def async_create_mcp_tools(mcp_server_url: str, use_resilient_wrapper: bool = True, max_retries: int = 2):
    """Create MCP tools by connecting to the server via Streamable HTTP transport using langchain-mcp-adapters.
    
    This function dynamically fetches available tools from the MCP server at runtime,
    using the MultiServerMCPClient from langchain-mcp-adapters which handles session ID issues
    that occur with direct MCP client usage.
    
    Args:
        mcp_server_url: The URL of the MCP server to connect to
        use_resilient_wrapper: Whether to wrap tools in ResilientMcpTool for better error handling
        max_retries: Maximum number of retries for resilient tools
        
    Returns:
        A list of tools available from the MCP server
    """
    logger.info(f"Connecting to MCP server: {mcp_server_url}")
    
    try:
        logger.debug("Setting up MultiServerMCPClient")
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
        logger.debug("Creating MultiServerMCPClient")
        client = MultiServerMCPClient(connections=connections)
        
        # Fetch all available tools from the MCP server
        logger.debug("Fetching available tools")
        tools = await client.get_tools()
        logger.info(f"Successfully connected to MCP server and retrieved {len(tools) if tools else 0} tools")
        
        # Print details about the tools for debugging
        if tools:
            for i, tool in enumerate(tools):
                logger.debug(f"Tool {i+1} - Name: {tool.name}")
                logger.debug(f"Tool {i+1} - Description: {tool.description[:50]}..." if len(tool.description) > 50 else tool.description)
            
            if use_resilient_wrapper:
                # Wrap each tool with the resilient wrapper
                resilient_tools = []
                for tool in tools:
                    resilient_tools.append(ResilientMcpTool(tool, max_retries=max_retries))
                logger.info(f"Created {len(resilient_tools)} resilient MCP tools with {max_retries} max retries")
                return resilient_tools
        
        return tools
    except Exception as e:
        logger.error(f"Failed connecting to MCP server: {str(e)}")
        import traceback
        logger.debug("Exception traceback:")
        logger.debug(traceback.format_exc())
        # Return empty list to allow the workflow to continue
        return []

def create_mcp_tools(mcp_server_url: str, use_resilient_wrapper: bool = True, max_retries: int = 2):
    """Create MCP tools synchronously.
    
    Args:
        mcp_server_url: The URL of the MCP server to connect to
        use_resilient_wrapper: Whether to wrap tools in ResilientMcpTool for better error handling
        max_retries: Maximum number of retries for resilient tools
        
    Returns:
        A list of tools available from the MCP server
    """
    return asyncio.run(async_create_mcp_tools(mcp_server_url, use_resilient_wrapper, max_retries))
