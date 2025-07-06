# MCP Servers Management

This guide covers how to manage Model Context Protocol (MCP) servers in the A2A LangGraph Boilerplate, including setup, configuration, and integration with AI agents.

## What is MCP?

Model Context Protocol (MCP) is a universal standard for connecting AI assistants to external data sources and tools. MCP servers provide:

- **Tool Integration**: Access to external APIs and services
- **Resource Management**: File system, database, and web resources
- **Prompt Templates**: Reusable prompt patterns
- **Standardized Interface**: Uniform way to interact with diverse tools

## MCP Architecture

### Components

1. **MCP Server**: External service providing tools and resources
2. **MCP Client**: Built into the A2A system for connecting to servers  
3. **Tools**: Specific functions exposed by MCP servers
4. **Transport**: Communication layer (currently supports Streamable HTTP)

### Communication Flow

```
AI Agent → LangGraph → MCP Client → MCP Server → External Service
                ←                 ←           ←
```

## Creating MCP Servers

### Basic MCP Server Registration

```python
import requests

mcp_server_data = {
    "name": "Search API",
    "url": "https://searchapi-mcp.prod.diginext.site/mcp",
    "description": "Web search and information retrieval capabilities"
}

response = requests.post("http://localhost:8000/mcp_servers/", json=mcp_server_data)
mcp_server = response.json()
print(f"Created MCP server: {mcp_server['id']}")
```

### MCP Server with Authentication

```python
# Note: Authentication headers are configured in the server connection
mcp_server_data = {
    "name": "Authenticated API",
    "url": "https://api.example.com/mcp",
    "description": "API requiring authentication",
    # Authentication is handled in the connection configuration
}

response = requests.post("http://localhost:8000/mcp_servers/", json=mcp_server_data)
```

### Multiple MCP Servers

```python
# Configure multiple servers for different capabilities
mcp_servers = [
    {
        "name": "Search API",
        "url": "https://searchapi-mcp.prod.diginext.site/mcp",
        "description": "Web search capabilities"
    },
    {
        "name": "File System",
        "url": "https://filesystem-mcp.example.com/mcp", 
        "description": "File system operations"
    },
    {
        "name": "Database API",
        "url": "https://database-mcp.example.com/mcp",
        "description": "Database query and management"
    }
]

# Create each server
for server_data in mcp_servers:
    response = requests.post("http://localhost:8000/mcp_servers/", json=server_data)
    server = response.json()
    print(f"Created server: {server['name']}")
```

## Exploring MCP Server Capabilities

### Discover Available Tools

```python
# Get tools from a specific MCP server
server_id = "mcp-server-uuid-here"
response = requests.get(f"http://localhost:8000/mcp_servers/{server_id}/tools")
tools = response.json()

print(f"Available tools: {len(tools)}")
for tool in tools:
    print(f"- {tool['name']}: {tool['description']}")
```

### Discover Resources

```python
# Get resources from MCP server
response = requests.get(f"http://localhost:8000/mcp_servers/{server_id}/resources")
resources = response.json()

print(f"Available resources: {len(resources)}")
for resource in resources:
    print(f"- {resource['name']}: {resource['description']}")
```

### Discover Prompts

```python
# Get prompt templates from MCP server
response = requests.get(f"http://localhost:8000/mcp_servers/{server_id}/prompts")
prompts = response.json()

print(f"Available prompts: {len(prompts)}")
for prompt in prompts:
    print(f"- {prompt['name']}: {prompt['description']}")
```

## Tool Management

### Creating Tools from MCP Servers

```python
# Create tools based on MCP server capabilities
def create_tools_from_mcp_server(mcp_server_id):
    # Get available tools from the server
    response = requests.get(f"http://localhost:8000/mcp_servers/{mcp_server_id}/tools")
    mcp_tools = response.json()
    
    created_tools = []
    for mcp_tool in mcp_tools:
        tool_data = {
            "name": mcp_tool["name"],
            "description": mcp_tool["description"],
            "api_name": mcp_tool["name"],  # Use the MCP tool name as API name
            "mcp_server_id": mcp_server_id
        }
        
        response = requests.post("http://localhost:8000/tools/", json=tool_data)
        tool = response.json()
        created_tools.append(tool)
        print(f"Created tool: {tool['name']}")
    
    return created_tools

# Create tools from a specific MCP server
tools = create_tools_from_mcp_server(mcp_server_id)
```

### Tool Configuration Examples

#### Search Tool

```python
search_tool = {
    "name": "web_search",
    "description": "Search the web for current information and news",
    "api_name": "search",
    "mcp_server_id": search_mcp_server_id,
    "parameters": {
        "query": {
            "type": "string",
            "description": "Search query terms",
            "required": True
        },
        "num_results": {
            "type": "integer", 
            "description": "Number of results to return",
            "default": 10
        }
    }
}
```

#### File System Tool

```python
file_tool = {
    "name": "read_file",
    "description": "Read contents of a file from the file system",
    "api_name": "read_file",
    "mcp_server_id": filesystem_mcp_server_id,
    "parameters": {
        "file_path": {
            "type": "string",
            "description": "Path to the file to read",
            "required": True
        }
    }
}
```

#### Database Tool

```python
database_tool = {
    "name": "query_database",
    "description": "Execute SQL queries against the database",
    "api_name": "execute_query",
    "mcp_server_id": database_mcp_server_id,
    "parameters": {
        "query": {
            "type": "string",
            "description": "SQL query to execute",
            "required": True
        },
        "limit": {
            "type": "integer",
            "description": "Maximum number of rows to return",
            "default": 100
        }
    }
}
```

## MCP Server Configuration

### Connection Management

The system uses `langchain-mcp-adapters` for robust MCP server connections:

```python
# Connection configuration (handled internally)
connections = {
    "search_api": {
        "url": "https://searchapi-mcp.prod.diginext.site/mcp",
        "transport": "streamable_http",
        "headers": {}  # Authentication headers if needed
    }
}
```

### Resilient Tool Wrapper

The system includes a resilient wrapper for MCP tools that provides:

- **Timeout handling**: Prevents hanging operations
- **Retry logic**: Automatic retries for transient failures
- **Graceful error handling**: User-friendly error messages
- **Connection recovery**: Automatic reconnection attempts

### Error Handling

```python
# Example of resilient tool behavior
class ResilientMcpTool:
    def __init__(self, base_tool, max_retries=2, retry_delay=1.0):
        self.base_tool = base_tool
        self.max_retries = max_retries
        self.retry_delay = retry_delay
    
    async def execute(self, **kwargs):
        for attempt in range(self.max_retries + 1):
            try:
                return await self.base_tool.execute(**kwargs)
            except Exception as e:
                if attempt < self.max_retries:
                    await asyncio.sleep(self.retry_delay)
                else:
                    return f"Error: Tool execution failed after {self.max_retries + 1} attempts"
```

## Authentication and Security

### API Key Configuration

For MCP servers requiring authentication:

```bash
# In .env file
SEARCH_API_KEY="your-search-api-key"
DATABASE_API_KEY="your-database-api-key"
CUSTOM_SERVICE_TOKEN="your-service-token"
```

### Authentication Headers

```python
# Configure authentication in MCP client (handled internally)
auth_headers = {
    "Authorization": f"Bearer {os.getenv('SEARCH_API_KEY')}",
    "X-API-Key": os.getenv('CUSTOM_SERVICE_TOKEN')
}
```

### Security Best Practices

1. **Use Environment Variables**: Store sensitive data in `.env` files
2. **Validate Inputs**: Sanitize all inputs to MCP tools
3. **Access Control**: Limit which agents can access which tools
4. **Audit Logging**: Log all MCP tool usage for security monitoring

## Monitoring MCP Servers

### Health Checks

```python
async def check_mcp_server_health(mcp_server_id):
    """Check if an MCP server is responding."""
    try:
        response = requests.get(f"http://localhost:8000/mcp_servers/{mcp_server_id}/tools")
        if response.status_code == 200:
            tools = response.json()
            return {
                "status": "healthy",
                "tools_count": len(tools),
                "response_time": response.elapsed.total_seconds()
            }
        else:
            return {"status": "error", "error": f"HTTP {response.status_code}"}
    except Exception as e:
        return {"status": "error", "error": str(e)}

# Check all MCP servers
response = requests.get("http://localhost:8000/mcp_servers/")
servers = response.json()

for server in servers:
    health = await check_mcp_server_health(server['id'])
    print(f"Server {server['name']}: {health['status']}")
```

### Performance Monitoring

```python
# Monitor MCP tool usage and performance
def monitor_mcp_performance():
    metrics = {
        "total_calls": 0,
        "successful_calls": 0,
        "failed_calls": 0,
        "average_response_time": 0,
        "error_rate": 0
    }
    
    # Collect metrics from logs or monitoring system
    return metrics
```

## Troubleshooting MCP Servers

### Common Issues

#### 1. Connection Errors

```python
# Symptoms: Unable to connect to MCP server
# Solutions:
# - Verify server URL is correct and accessible
# - Check network connectivity
# - Validate authentication credentials
# - Review firewall settings

async def diagnose_connection(mcp_server_url):
    try:
        # Test basic HTTP connectivity
        async with httpx.AsyncClient() as client:
            response = await client.get(mcp_server_url)
            return f"HTTP response: {response.status_code}"
    except Exception as e:
        return f"Connection failed: {str(e)}"
```

#### 2. Authentication Failures

```python
# Symptoms: 401 Unauthorized errors
# Solutions:
# - Verify API keys are correct
# - Check authentication header format
# - Ensure credentials have proper permissions
# - Validate token expiration

def check_authentication(api_key):
    if not api_key:
        return "Missing API key"
    if len(api_key) < 10:
        return "API key appears invalid (too short)"
    return "API key format looks valid"
```

#### 3. Tool Discovery Issues

```python
# Symptoms: No tools found or empty tool list
# Solutions:
# - Verify MCP server implements tools endpoint
# - Check server configuration
# - Review server logs for errors

async def diagnose_tools(mcp_server_id):
    try:
        response = requests.get(f"http://localhost:8000/mcp_servers/{mcp_server_id}/tools")
        tools = response.json()
        
        if isinstance(tools, list):
            return f"Found {len(tools)} tools"
        else:
            return f"Unexpected response format: {type(tools)}"
    except Exception as e:
        return f"Tool discovery failed: {str(e)}"
```

#### 4. Timeout Issues

```python
# Symptoms: Operations timeout or hang
# Solutions:
# - Increase timeout values
# - Optimize MCP server performance
# - Implement connection pooling
# - Use asynchronous operations

# Configure timeouts
TIMEOUT_SETTINGS = {
    "connection_timeout": 30.0,
    "read_timeout": 60.0,
    "total_timeout": 120.0
}
```

### Debugging Steps

1. **Verify Server Accessibility**
   ```bash
   curl -I https://searchapi-mcp.prod.diginext.site/mcp
   ```

2. **Check Authentication**
   ```bash
   curl -H "Authorization: Bearer your-token" https://api.example.com/mcp
   ```

3. **Test Tool Discovery**
   ```python
   response = requests.get(f"http://localhost:8000/mcp_servers/{server_id}/tools")
   print(response.status_code, response.json())
   ```

4. **Review Logs**
   ```bash
   tail -f server.log | grep "MCP"
   ```

## Advanced MCP Features

### Custom MCP Servers

You can create custom MCP servers for specific needs:

```python
# Example custom MCP server configuration
custom_server = {
    "name": "Company API",
    "url": "https://internal-api.company.com/mcp",
    "description": "Internal company tools and data",
    "capabilities": [
        "employee_lookup",
        "project_status",
        "resource_booking"
    ]
}
```

### Dynamic Tool Loading

The system supports dynamic tool loading at runtime:

```python
# Tools are loaded dynamically when crews execute prompts
async def load_mcp_tools_dynamically():
    # Get all MCP servers from database
    mcp_servers = db.query(McpServer).all()
    
    # Create tools from all available servers
    all_tools = []
    for server in mcp_servers:
        server_tools = await async_create_mcp_tools(server.url)
        all_tools.extend(server_tools)
    
    return all_tools
```

### Tool Caching

For performance optimization:

```python
# Cache frequently used tools
from functools import lru_cache

@lru_cache(maxsize=128)
def get_cached_mcp_tools(server_url):
    return create_mcp_tools(server_url)
```

## Best Practices

### Server Management

1. **Regular Health Checks**: Monitor server availability
2. **Performance Monitoring**: Track response times and success rates
3. **Version Management**: Keep track of MCP server versions
4. **Backup Configurations**: Maintain backup configurations for critical servers

### Tool Organization

1. **Logical Grouping**: Group related tools by functionality
2. **Clear Naming**: Use descriptive names for tools
3. **Documentation**: Maintain clear descriptions for all tools
4. **Testing**: Regularly test tool functionality

### Security

1. **Access Control**: Limit tool access based on agent roles
2. **Input Validation**: Sanitize all inputs to MCP tools
3. **Audit Logging**: Log all MCP tool usage
4. **Credential Management**: Use secure credential storage

### Performance

1. **Connection Pooling**: Reuse connections where possible
2. **Caching**: Cache frequently accessed data
3. **Timeouts**: Set appropriate timeouts for all operations
4. **Monitoring**: Monitor performance metrics continuously

This comprehensive approach to MCP server management ensures reliable, secure, and efficient integration of external tools and services with your AI agent system.