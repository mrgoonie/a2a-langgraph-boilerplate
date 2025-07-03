import os
import asyncio
from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient

# Load environment variables
load_dotenv()

async def test_langchain_mcp_adapters():
    """Test connecting to MCP server using langchain-mcp-adapters"""
    print("Testing connection to MCP server using langchain-mcp-adapters...")
    
    # Try with the ReviewWeb MCP server URL
    mcp_server_url = "https://mcpservers-reviewwebmcp.prod.diginext.site/mcp"
    
    # Setup connection configuration
    connections = {
        "reviewweb": {
            "url": mcp_server_url,
            "transport": "streamable_http",
            # Add headers if needed, e.g. for auth
            "headers": {}
        }
    }
    
    try:
        print(f"- Connecting to MCP server: {mcp_server_url}")
        # Initialize the MultiServerMCPClient with the connection config
        client = MultiServerMCPClient(connections=connections)
        
        print("- Loading all available tools...")
        # Load all available tools from the MCP server
        tools = await client.get_tools()
        
        print(f"- SUCCESS! Retrieved {len(tools)} tools")
        # Display tools
        for i, tool in enumerate(tools):
            print(f"  Tool {i+1}: {tool.name}")
            print(f"    Description: {tool.description}")
            print(f"    Args: {getattr(tool, 'args_schema', None)}")
        
        print("\nConnection test successful!")
        return tools
        
    except Exception as e:
        print(f"- ERROR: {str(e)}")
        print(f"- Connection test failed")
        return None

if __name__ == "__main__":
    asyncio.run(test_langchain_mcp_adapters())
