# Getting Started

This guide will help you set up and run the A2A LangGraph Boilerplate project for building AI agent clusters.

## Prerequisites

- Python 3.13 or higher
- PostgreSQL database
- OpenRouter API key
- Virtual environment tool (venv)

## Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd a2a-langgraph-boilerplate
```

### 2. Set Up Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Environment Configuration

Create a `.env` file in the project root:

```env
DATABASE_URL="postgresql://username:password@localhost:5432/database_name"
OPENROUTER_API_KEY="your_openrouter_api_key_here"
```

### 5. Database Setup

Create and initialize the database:

```bash
python create_tables.py
```

This will create all necessary tables for crews, agents, MCP servers, tools, and conversations.

## Running the Application

### Development Server

Start the FastAPI development server:

```bash
uvicorn app.main:app --reload --log-level info
```

The application will be available at `http://localhost:8000`

### Background Logging

To run the server with logging to a file:

```bash
uvicorn app.main:app --reload --log-level info > server.log 2>&1 &
```

## API Documentation

Once the server is running, you can access the interactive API documentation:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## Project Structure

```
a2a-langgraph-boilerplate/
├── app/                    # Main application directory
│   ├── api/               # API endpoints
│   ├── core/              # Core logic and LangGraph setup
│   ├── models/            # Database models
│   ├── schemas/           # Pydantic schemas
│   └── services/          # Business logic services
├── docs/                  # Documentation
├── tests/                 # Test files
├── requirements.txt       # Python dependencies
├── create_tables.py       # Database setup script
└── .env                   # Environment variables
```

## Quick Start Example

### 1. Create an AI Crew

```bash
curl -X POST "http://localhost:8000/crews/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Research Team",
    "description": "A team of AI agents for research tasks"
  }'
```

### 2. Create an Agent

```bash
curl -X POST "http://localhost:8000/agents/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Research Agent",
    "description": "An agent specialized in research tasks",
    "role": "researcher",
    "system_instructions": "You are a research assistant...",
    "crew_id": "crew-uuid-here"
  }'
```

### 3. Create an MCP Server

```bash
curl -X POST "http://localhost:8000/mcp_servers/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Search API",
    "url": "https://searchapi-mcp.prod.diginext.site/mcp",
    "description": "Search API MCP server for web search capabilities"
  }'
```

### 4. Create a Tool

```bash
curl -X POST "http://localhost:8000/tools/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "web_search",
    "description": "Search the web for information",
    "api_name": "search",
    "mcp_server_id": "mcp-server-uuid-here"
  }'
```

### 5. Add Tool to Agent

```bash
curl -X POST "http://localhost:8000/agents/{agent_id}/tools/{tool_id}" \
  -H "Content-Type: application/json"
```

## Testing

Run the test suite:

```bash
pytest
```

Run specific test files:

```bash
pytest tests/test_crews.py
pytest tests/test_agents.py
```

## Key Features

### AI Crew Management
- Create and manage AI crews (collections of agents)
- Each crew has a supervisor agent that coordinates tasks
- Support for multi-agent collaboration

### Agent Management
- Create specialized AI agents with custom roles
- Assign tools and capabilities to agents
- Configure system instructions for agent behavior

### MCP Server Integration
- Connect to Model Context Protocol (MCP) servers
- Integrate external tools and APIs
- Support for tool discovery and execution

### Conversation Management
- Track conversations between users and AI crews
- Store conversation history and context
- Support for streaming responses

## Troubleshooting

### Common Issues

1. **Database Connection Error**
   - Verify PostgreSQL is running
   - Check DATABASE_URL in .env file
   - Ensure database exists and is accessible

2. **OpenRouter API Error**
   - Verify OPENROUTER_API_KEY is set correctly
   - Check API key permissions and credits

3. **MCP Server Connection Error**
   - Verify MCP server URL is accessible
   - Check if authentication is required for the MCP server

### Logs

Check the server logs for detailed error information:

```bash
tail -f server.log
```

## Next Steps

- Read the [API Documentation](api-endpoints.md) for detailed endpoint information
- Learn about [AI Crew Management](ai-crews-management.md)
- Explore [MCP Server Integration](mcp-servers-management.md)
- Check the [Testing Guide](testing.md) for comprehensive testing information

## Support

For issues and questions:
- Check the existing documentation
- Review the test files for usage examples
- Examine the example scripts in the project root