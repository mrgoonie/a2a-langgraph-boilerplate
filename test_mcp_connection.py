import os
import asyncio
import inspect
import json
from contextlib import AsyncExitStack
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def inspect_streamable_http_client():
    """Inspect the streamable HTTP client to understand how session ID is handled"""
    print("\nInspecting streamablehttp_client implementation...")
    print(f"Source file: {inspect.getfile(streamablehttp_client)}")
    
    # Try to determine if there's a bug in the session ID handling
    print("\nChecking ClientSession initialization...")
    try:
        source = inspect.getsource(ClientSession.__init__)
        print(f"ClientSession.__init__ source:\n{source}")
    except Exception as e:
        print(f"Could not get source: {e}")

async def test_mcp_connection(mcp_server_url: str):
    """Test connecting to an MCP server with focus on session ID handling"""
    print(f"Testing connection to MCP server: {mcp_server_url}")
    
    # First, inspect the client implementation
    await inspect_streamable_http_client()
    
    # Try with manual session ID handling
    print("\nAttempting connection with manual session ID handling...")
    try:
        async with AsyncExitStack() as stack:
            print("- Connecting to MCP server...")
            read, write, get_session_id = await stack.enter_async_context(
                streamablehttp_client(url=mcp_server_url)
            )
            
            # Debug the session ID and its type
            session_id = get_session_id()
            print(f"- Raw session ID: {repr(session_id)}, Type: {type(session_id)}")
            
            if session_id is None:
                print("- WARNING: Session ID is None, which will likely cause authentication failures")
                print("- Attempting to workaround by manually setting headers...")
                
                # Try to create a custom client that doesn't rely on session ID
                print("- Creating custom ClientSession...")
                session = ClientSession(read, write)
                
                print("- Manually initializing session...")
                try:
                    # Attempt to initialize without relying on session ID
                    await session.initialize()
                    print("- Session initialized despite None session ID!")
                    
                    # Debug session internals if possible
                    print(f"- Session attributes: {dir(session)}")
                except Exception as e:
                    print(f"- Session initialization failed: {e}")
                    return
            else:
                # Normal flow with valid session ID
                print("- Creating ClientSession...")
                session = ClientSession(read, write)
                
                print("- Initializing session...")
                await session.initialize()
                print("- Session initialized successfully!")
            
            # Try to list tools
            try:
                print("- Fetching available tools...")
                tools = await session.list_tools()
                print(f"- SUCCESS! Retrieved {len(tools)} tools")
                
                # Display tools
                for i, tool in enumerate(tools):
                    print(f"  Tool {i+1}: {getattr(tool, 'name', 'Unknown')}")
            except Exception as e:
                print(f"- Tool listing failed: {e}")
    
    except Exception as e:
        print(f"- Connection failed: {str(e)}")
    
    print("\nConnection test complete")

if __name__ == "__main__":
    # Try with the SearchAPI MCP server URL
    # mcp_server_url = "https://searchapi-mcp.prod.diginext.site/mcp"
    mcp_server_url = "https://mcpservers-reviewwebmcp.prod.diginext.site/mcp"
    asyncio.run(test_mcp_connection(mcp_server_url))
