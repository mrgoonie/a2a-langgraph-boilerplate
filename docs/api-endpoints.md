# API Endpoints

This document provides comprehensive information about all API endpoints available in the A2A LangGraph Boilerplate.

## Base URL

When running locally: `http://localhost:8000`

## Authentication

Currently, the API does not require authentication. All endpoints are publicly accessible.

## Response Format

All responses follow standard HTTP status codes:
- `200` - Success
- `201` - Created
- `400` - Bad Request
- `404` - Not Found
- `422` - Validation Error
- `500` - Internal Server Error

## API Documentation

Interactive API documentation is available at:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## Endpoints

### Root Endpoint

#### GET /
Welcome message endpoint.

**Response:**
```json
{
  "message": "Welcome to the Multi AI Agents System Boilerplate"
}
```

---

## Crews Management

### POST /crews/
Create a new AI crew.

**Request Body:**
```json
{
  "name": "Research Team",
  "description": "A team of AI agents for research tasks"
}
```

**Response:**
```json
{
  "id": "uuid",
  "name": "Research Team",
  "description": "A team of AI agents for research tasks",
  "created_at": "2023-07-06T12:00:00Z",
  "updated_at": "2023-07-06T12:00:00Z"
}
```

### GET /crews/
Get all AI crews.

**Query Parameters:**
- `skip` (int, optional): Number of records to skip (default: 0)
- `limit` (int, optional): Maximum number of records to return (default: 100)

**Response:**
```json
[
  {
    "id": "uuid",
    "name": "Research Team",
    "description": "A team of AI agents for research tasks",
    "created_at": "2023-07-06T12:00:00Z",
    "updated_at": "2023-07-06T12:00:00Z"
  }
]
```

### GET /crews/{crew_id}
Get a specific AI crew by ID.

**Path Parameters:**
- `crew_id` (UUID): The crew ID

**Response:**
```json
{
  "id": "uuid",
  "name": "Research Team",
  "description": "A team of AI agents for research tasks",
  "created_at": "2023-07-06T12:00:00Z",
  "updated_at": "2023-07-06T12:00:00Z"
}
```

### PUT /crews/{crew_id}
Update an existing AI crew.

**Path Parameters:**
- `crew_id` (UUID): The crew ID

**Request Body:**
```json
{
  "name": "Updated Research Team",
  "description": "Updated description"
}
```

**Response:**
```json
{
  "id": "uuid",
  "name": "Updated Research Team",
  "description": "Updated description",
  "created_at": "2023-07-06T12:00:00Z",
  "updated_at": "2023-07-06T12:30:00Z"
}
```

### DELETE /crews/{crew_id}
Delete an AI crew.

**Path Parameters:**
- `crew_id` (UUID): The crew ID

**Response:**
```json
{
  "id": "uuid",
  "name": "Research Team",
  "description": "A team of AI agents for research tasks",
  "created_at": "2023-07-06T12:00:00Z",
  "updated_at": "2023-07-06T12:00:00Z"
}
```

### POST /crews/{crew_id}/execute
Execute a prompt using the AI crew.

**Path Parameters:**
- `crew_id` (UUID): The crew ID

**Request Body:**
```json
{
  "content": "Research the latest trends in AI technology"
}
```

**Response:**
```json
{
  "result": "AI research results...",
  "metadata": {
    "execution_time": "5.2s",
    "agents_used": ["researcher", "summarizer"]
  }
}
```

---

## Agents Management

### POST /agents/
Create a new AI agent.

**Request Body:**
```json
{
  "name": "Research Agent",
  "description": "An agent specialized in research tasks",
  "role": "researcher",
  "system_instructions": "You are a research assistant specialized in finding and analyzing information.",
  "crew_id": "uuid"
}
```

**Response:**
```json
{
  "id": "uuid",
  "name": "Research Agent",
  "description": "An agent specialized in research tasks",
  "role": "researcher",
  "system_instructions": "You are a research assistant...",
  "crew_id": "uuid",
  "created_at": "2023-07-06T12:00:00Z",
  "updated_at": "2023-07-06T12:00:00Z"
}
```

### GET /agents/
Get all AI agents.

**Query Parameters:**
- `skip` (int, optional): Number of records to skip (default: 0)
- `limit` (int, optional): Maximum number of records to return (default: 100)

**Response:**
```json
[
  {
    "id": "uuid",
    "name": "Research Agent",
    "description": "An agent specialized in research tasks",
    "role": "researcher",
    "system_instructions": "You are a research assistant...",
    "crew_id": "uuid",
    "created_at": "2023-07-06T12:00:00Z",
    "updated_at": "2023-07-06T12:00:00Z"
  }
]
```

### GET /agents/{agent_id}
Get a specific AI agent by ID.

**Path Parameters:**
- `agent_id` (UUID): The agent ID

**Response:**
```json
{
  "id": "uuid",
  "name": "Research Agent",
  "description": "An agent specialized in research tasks",
  "role": "researcher",
  "system_instructions": "You are a research assistant...",
  "crew_id": "uuid",
  "created_at": "2023-07-06T12:00:00Z",
  "updated_at": "2023-07-06T12:00:00Z"
}
```

### PUT /agents/{agent_id}
Update an existing AI agent.

**Path Parameters:**
- `agent_id` (UUID): The agent ID

**Request Body:**
```json
{
  "name": "Updated Research Agent",
  "description": "Updated description",
  "role": "senior_researcher",
  "system_instructions": "Updated instructions...",
  "crew_id": "uuid"
}
```

**Response:**
```json
{
  "id": "uuid",
  "name": "Updated Research Agent",
  "description": "Updated description",
  "role": "senior_researcher",
  "system_instructions": "Updated instructions...",
  "crew_id": "uuid",
  "created_at": "2023-07-06T12:00:00Z",
  "updated_at": "2023-07-06T12:30:00Z"
}
```

### DELETE /agents/{agent_id}
Delete an AI agent.

**Path Parameters:**
- `agent_id` (UUID): The agent ID

**Response:**
```json
{
  "id": "uuid",
  "name": "Research Agent",
  "description": "An agent specialized in research tasks",
  "role": "researcher",
  "system_instructions": "You are a research assistant...",
  "crew_id": "uuid",
  "created_at": "2023-07-06T12:00:00Z",
  "updated_at": "2023-07-06T12:00:00Z"
}
```

### POST /agents/{agent_id}/tools/{tool_id}
Add a tool to an AI agent.

**Path Parameters:**
- `agent_id` (UUID): The agent ID
- `tool_id` (UUID): The tool ID

**Response:**
```json
{
  "id": "uuid",
  "name": "Research Agent",
  "description": "An agent specialized in research tasks",
  "role": "researcher",
  "system_instructions": "You are a research assistant...",
  "crew_id": "uuid",
  "tools": [
    {
      "id": "uuid",
      "name": "web_search",
      "description": "Search the web for information"
    }
  ],
  "created_at": "2023-07-06T12:00:00Z",
  "updated_at": "2023-07-06T12:30:00Z"
}
```

---

## MCP Servers Management

### POST /mcp_servers/
Create a new MCP server.

**Request Body:**
```json
{
  "name": "Search API",
  "url": "https://searchapi-mcp.prod.diginext.site/mcp",
  "description": "Search API MCP server for web search capabilities"
}
```

**Response:**
```json
{
  "id": "uuid",
  "name": "Search API",
  "url": "https://searchapi-mcp.prod.diginext.site/mcp",
  "description": "Search API MCP server for web search capabilities",
  "created_at": "2023-07-06T12:00:00Z",
  "updated_at": "2023-07-06T12:00:00Z"
}
```

### GET /mcp_servers/
Get all MCP servers.

**Query Parameters:**
- `skip` (int, optional): Number of records to skip (default: 0)
- `limit` (int, optional): Maximum number of records to return (default: 100)

**Response:**
```json
[
  {
    "id": "uuid",
    "name": "Search API",
    "url": "https://searchapi-mcp.prod.diginext.site/mcp",
    "description": "Search API MCP server for web search capabilities",
    "created_at": "2023-07-06T12:00:00Z",
    "updated_at": "2023-07-06T12:00:00Z"
  }
]
```

### GET /mcp_servers/{mcp_server_id}
Get a specific MCP server by ID.

**Path Parameters:**
- `mcp_server_id` (UUID): The MCP server ID

**Response:**
```json
{
  "id": "uuid",
  "name": "Search API",
  "url": "https://searchapi-mcp.prod.diginext.site/mcp",
  "description": "Search API MCP server for web search capabilities",
  "created_at": "2023-07-06T12:00:00Z",
  "updated_at": "2023-07-06T12:00:00Z"
}
```

### PUT /mcp_servers/{mcp_server_id}
Update an existing MCP server.

**Path Parameters:**
- `mcp_server_id` (UUID): The MCP server ID

**Request Body:**
```json
{
  "name": "Updated Search API",
  "url": "https://updated-searchapi-mcp.prod.diginext.site/mcp",
  "description": "Updated description"
}
```

**Response:**
```json
{
  "id": "uuid",
  "name": "Updated Search API",
  "url": "https://updated-searchapi-mcp.prod.diginext.site/mcp",
  "description": "Updated description",
  "created_at": "2023-07-06T12:00:00Z",
  "updated_at": "2023-07-06T12:30:00Z"
}
```

### DELETE /mcp_servers/{mcp_server_id}
Delete an MCP server.

**Path Parameters:**
- `mcp_server_id` (UUID): The MCP server ID

**Response:**
```json
{
  "id": "uuid",
  "name": "Search API",
  "url": "https://searchapi-mcp.prod.diginext.site/mcp",
  "description": "Search API MCP server for web search capabilities",
  "created_at": "2023-07-06T12:00:00Z",
  "updated_at": "2023-07-06T12:00:00Z"
}
```

### GET /mcp_servers/{mcp_server_id}/tools
Get available tools from a specific MCP server.

**Path Parameters:**
- `mcp_server_id` (UUID): The MCP server ID

**Response:**
```json
[
  {
    "name": "search",
    "description": "Search the web for information",
    "inputSchema": {
      "type": "object",
      "properties": {
        "query": {
          "type": "string",
          "description": "Search query"
        }
      }
    }
  }
]
```

### GET /mcp_servers/{mcp_server_id}/resources
Get available resources from a specific MCP server.

**Path Parameters:**
- `mcp_server_id` (UUID): The MCP server ID

**Response:**
```json
[
  {
    "uri": "resource://search-results",
    "name": "Search Results",
    "description": "Web search results",
    "mimeType": "application/json"
  }
]
```

### GET /mcp_servers/{mcp_server_id}/prompts
Get available prompts from a specific MCP server.

**Path Parameters:**
- `mcp_server_id` (UUID): The MCP server ID

**Response:**
```json
[
  {
    "name": "search_prompt",
    "description": "Template for search queries",
    "arguments": [
      {
        "name": "query",
        "description": "Search query",
        "required": true
      }
    ]
  }
]
```

---

## Tools Management

### POST /tools/
Create a new tool.

**Request Body:**
```json
{
  "name": "web_search",
  "description": "Search the web for information",
  "api_name": "search",
  "mcp_server_id": "uuid"
}
```

**Response:**
```json
{
  "id": "uuid",
  "name": "web_search",
  "description": "Search the web for information",
  "api_name": "search",
  "mcp_server_id": "uuid",
  "created_at": "2023-07-06T12:00:00Z",
  "updated_at": "2023-07-06T12:00:00Z"
}
```

### GET /tools/
Get all tools.

**Query Parameters:**
- `skip` (int, optional): Number of records to skip (default: 0)
- `limit` (int, optional): Maximum number of records to return (default: 100)

**Response:**
```json
[
  {
    "id": "uuid",
    "name": "web_search",
    "description": "Search the web for information",
    "api_name": "search",
    "mcp_server_id": "uuid",
    "created_at": "2023-07-06T12:00:00Z",
    "updated_at": "2023-07-06T12:00:00Z"
  }
]
```

### GET /tools/{tool_id}
Get a specific tool by ID.

**Path Parameters:**
- `tool_id` (UUID): The tool ID

**Response:**
```json
{
  "id": "uuid",
  "name": "web_search",
  "description": "Search the web for information",
  "api_name": "search",
  "mcp_server_id": "uuid",
  "created_at": "2023-07-06T12:00:00Z",
  "updated_at": "2023-07-06T12:00:00Z"
}
```

### PUT /tools/{tool_id}
Update an existing tool.

**Path Parameters:**
- `tool_id` (UUID): The tool ID

**Request Body:**
```json
{
  "name": "updated_web_search",
  "description": "Updated description",
  "api_name": "updated_search",
  "mcp_server_id": "uuid"
}
```

**Response:**
```json
{
  "id": "uuid",
  "name": "updated_web_search",
  "description": "Updated description",
  "api_name": "updated_search",
  "mcp_server_id": "uuid",
  "created_at": "2023-07-06T12:00:00Z",
  "updated_at": "2023-07-06T12:30:00Z"
}
```

### DELETE /tools/{tool_id}
Delete a tool.

**Path Parameters:**
- `tool_id` (UUID): The tool ID

**Response:**
```json
{
  "id": "uuid",
  "name": "web_search",
  "description": "Search the web for information",
  "api_name": "search",
  "mcp_server_id": "uuid",
  "created_at": "2023-07-06T12:00:00Z",
  "updated_at": "2023-07-06T12:00:00Z"
}
```

---

## Conversations Management

### POST /conversations/
Create a new conversation.

**Request Body:**
```json
{
  "title": "Research Discussion",
  "crew_id": "uuid",
  "agent_id": "uuid"
}
```

**Response:**
```json
{
  "id": "uuid",
  "title": "Research Discussion",
  "crew_id": "uuid",
  "agent_id": "uuid",
  "created_at": "2023-07-06T12:00:00Z",
  "updated_at": "2023-07-06T12:00:00Z"
}
```

### GET /conversations/
Get all conversations.

**Query Parameters:**
- `skip` (int, optional): Number of records to skip (default: 0)
- `limit` (int, optional): Maximum number of records to return (default: 100)

**Response:**
```json
[
  {
    "id": "uuid",
    "title": "Research Discussion",
    "crew_id": "uuid",
    "agent_id": "uuid",
    "created_at": "2023-07-06T12:00:00Z",
    "updated_at": "2023-07-06T12:00:00Z"
  }
]
```

### GET /conversations/{conversation_id}
Get a specific conversation by ID.

**Path Parameters:**
- `conversation_id` (UUID): The conversation ID

**Response:**
```json
{
  "id": "uuid",
  "title": "Research Discussion",
  "crew_id": "uuid",
  "agent_id": "uuid",
  "created_at": "2023-07-06T12:00:00Z",
  "updated_at": "2023-07-06T12:00:00Z"
}
```

---

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Invalid request data"
}
```

### 404 Not Found
```json
{
  "detail": "Resource not found"
}
```

### 422 Validation Error
```json
{
  "detail": [
    {
      "loc": ["body", "name"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
```

---

## Usage Examples

### Creating a Complete Workflow

1. **Create a crew:**
```bash
curl -X POST "http://localhost:8000/crews/" \
  -H "Content-Type: application/json" \
  -d '{"name": "Research Team", "description": "AI research team"}'
```

2. **Create an agent:**
```bash
curl -X POST "http://localhost:8000/agents/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Researcher",
    "role": "researcher",
    "crew_id": "crew-uuid-here"
  }'
```

3. **Create MCP server:**
```bash
curl -X POST "http://localhost:8000/mcp_servers/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Search API",
    "url": "https://searchapi-mcp.prod.diginext.site/mcp"
  }'
```

4. **Create tool:**
```bash
curl -X POST "http://localhost:8000/tools/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "web_search",
    "api_name": "search",
    "mcp_server_id": "mcp-server-uuid-here"
  }'
```

5. **Add tool to agent:**
```bash
curl -X POST "http://localhost:8000/agents/agent-uuid/tools/tool-uuid"
```

6. **Execute prompt:**
```bash
curl -X POST "http://localhost:8000/crews/crew-uuid/execute" \
  -H "Content-Type: application/json" \
  -d '{"content": "Research AI trends"}'
```

### Error Handling

Always check response status codes and handle errors appropriately:

```python
import requests

response = requests.post("http://localhost:8000/crews/", json={"name": "Test Crew"})

if response.status_code == 200:
    crew = response.json()
    print(f"Created crew: {crew['id']}")
elif response.status_code == 422:
    errors = response.json()
    print(f"Validation errors: {errors['detail']}")
else:
    print(f"Error: {response.status_code}")
```