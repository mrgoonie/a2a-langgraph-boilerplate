# PROJECT_OVERVIEW.md

## Concept
* Each AI agent cluster can have multiple AI agent crews (AI Crews)
* Each AI crew can have multiple AI agent, leaded by a superviser (a default AI agent of an AI crew)
* Each AI agent can call tools via MCP servers integration

## How it works
* A supervisor agent will receive input (prompt) from a user via API call, then create a detailed plan with its current capabilities (AI agents underneat and their tools)
* Then request the AI agents to perform tasks via A2A protocol
* Wait for all AI agents finish given tasks
* Grab all the results, analyze and respond to user based on the original input prompt.


## Project Structure

```
.
├── AGENT_INSTRUCTIONS.md
├── app
│   ├── __init__.py
│   ├── api
│   │   ├── __init__.py
│   │   ├── agents.py
│   │   ├── conversations.py
│   │   ├── crews.py
│   │   ├── mcp_servers.py
│   │   └── tools.py
│   ├── core
│   │   ├── __init__.py
│   │   ├── agents.py
│   │   ├── database.py
│   │   ├── graph.py
│   │   ├── logging.py
│   │   └── tools.py
│   ├── main.py
│   ├── models
│   │   ├── __init__.py
│   │   ├── agent_tool.py
│   │   ├── agent.py
│   │   ├── base.py
│   │   ├── conversation.py
│   │   ├── crew.py
│   │   ├── mcp_server.py
│   │   ├── setup_relationships.py
│   │   └── tool.py
│   ├── schemas
│   │   ├── agent.py
│   │   ├── conversation.py
│   │   ├── crew.py
│   │   ├── mcp_server.py
│   │   ├── prompt.py
│   │   └── tool.py
│   └── services
│       ├── __init__.py
│       ├── agent.py
│       ├── conversation.py
│       ├── crew.py
│       ├── mcp_server.py
│       └── tool.py
├── create_tables.py
├── docs
│   └── UUID_MIGRATION.md
├── example_ai_crew_chat.py
├── example.py
├── GEMINI.md
├── LICENSE
├── PROJECT_OVERVIEW.md
├── README.md
├── requirements.txt
├── server.log
├── test_uuid_models.py
├── tests
│   ├── conftest.py
│   ├── test_agents.py
│   ├── test_ai_crew_chat.py
│   ├── test_conversations.py
│   ├── test_crews.py
│   ├── test_mcp_servers.py
│   └── test_tools.py
```

**Directories:**

*   `app`: The main application directory.
*   `app/api`: Contains the API endpoints for the application.
*   `app/core`: Houses the core logic of the application, including LangGraph setup and agent definitions.
*   `app/models`: Defines the database models for PostgreSQL.
*   `app/schemas`: Contains the Pydantic schemas for the API.
*   `app/services`: Contains services that interact with the database and other external resources.
*   `docs`: Contains project documentation files.
*   `tests`: Contains the tests for the application.
*   `.env`: Stores environment variables.
*   `create_tables.py`: A script to create the database tables.
*   `example.py`: An example script to test the LangGraph implementation.
*   `example_ai_crew_chat.py`: An example script demonstrating AI crew chat functionality.
*   `test_uuid_models.py`: A test script for UUID-based models and relationships.
*   `PROJECT_OVERVIEW.md`: This file.
*   `requirements.txt`: Lists the Python dependencies for the project.

## Features

*   [x] Create & manage AI crews
*   [x] Create & manage AI agents
*   [x] Create & manage MCP servers
*   [x] Create & manage Tools
*   [x] Integrate MCP servers for tool usage
*   [ ] Monitor activity logs (save/read/retention in database)
*   [x] Create & manage conversations with AI crews / AI agents
*   [x] Expose Swagger API Docs for frontend integration instructions
*   [x] Continuous integration with GitHub Actions
*   [x] UUID-based primary keys for all database models

## Dependencies

*   langchain
*   langgraph
*   fastapi
*   uvicorn
*   psycopg2-binary
*   sqlalchemy
*   python-dotenv
*   langchain-openai
*   tavily-python
*   langchain-community
*   pytest

## API Routes

*   `GET /`: Welcome message.
*   `POST /crews/`: Create a new crew.
*   `GET /crews/`: Get all crews.
*   `GET /crews/{crew_id}`: Get a crew by ID.
*   `PUT /crews/{crew_id}`: Update a crew.
*   `DELETE /crews/{crew_id}`: Delete a crew.
*   `POST /agents/`: Create a new agent.
*   `GET /agents/`: Get all agents.
*   `GET /agents/{agent_id}`: Get an agent by ID.
*   `PUT /agents/{agent_id}`: Update an agent.
*   `DELETE /agents/{agent_id}`: Delete an agent.
*   `POST /agents/{agent_id}/tools/{tool_id}`: Add a tool to an agent.
*   `POST /mcp_servers/`: Create a new MCP server.
*   `GET /mcp_servers/`: Get all MCP servers.
*   `GET /mcp_servers/{mcp_server_id}`: Get an MCP server by ID.
*   `PUT /mcp_servers/{mcp_server_id}`: Update an MCP server.
*   `DELETE /mcp_servers/{mcp_server_id}`: Delete an MCP server.
*   `POST /tools/`: Create a new tool.
*   `GET /tools/`: Get all tools.
*   `GET /tools/{tool_id}`: Get a tool by ID.
*   `PUT /tools/{tool_id}`: Update a tool.
*   `DELETE /tools/{tool_id}`: Delete a tool.
*   `POST /conversations/`: Create a new conversation.
*   `GET /conversations/`: Get all conversations.
*   `GET /conversations/{conversation_id}`: Get a conversation by ID.

## API Documentation

The API documentation is automatically generated by FastAPI and is available at the following URLs:

*   **Swagger UI:** `/docs`
*   **ReDoc:** `/redoc`

## Testing

To run the tests, you will need to install `pytest`:

```bash
pip install pytest
```

Then, you can run the tests using the following command:

```bash
pytest
```

## Todos

*   [ ] Implement true A2A communication between agents.
    *   [ ] Modify the `AgentGraph` to allow agents to directly communicate with each other.
    *   [ ] Update the supervisor logic to delegate tasks to agents and manage the overall workflow.
    *   [ ] Create a new agent type, "supervisor", to distinguish it from other agents.
    *   [ ] Update the API to allow creating crews with a supervisor and multiple agents.
    *   [ ] Update the `AGENT_INSTRUCTIONS.md` file with instructions on how to create a crew with a supervisor and multiple agents.

## Changelog

*   **2025-07-03:**
    *   Migrated all database models from integer primary keys to UUIDs for improved scalability and security.
    *   Implemented late-binding relationship setup to resolve circular dependencies between models.
    *   Added comprehensive UUID model tests.
    *   Added documentation for UUID migration in `docs/UUID_MIGRATION.md`.
    *   Enhanced error handling and validation for UUID operations in API routes and services.

*   **2025-07-02:**
    *   Added tests for all endpoints and workflows.
    *   Added a GitHub Actions workflow to run the tests automatically.
    *   Added A2A implementation to the project's roadmap.
    *   Initial project setup.
    *   Created database models for `Crew`, `Agent`, `McpServer`, and `Tool`.
    *   Set up the database connection and created the tables.
    *   Implemented the core LangGraph logic for agent interaction.
    *   Created API endpoints for managing crews.
    *   Created API endpoints for managing agents.
    *   Created API endpoints for managing MCP servers.
    *   Created API endpoints for managing tools.
    *   Integrated MCP servers for tool usage.
    *   Updated the database schema to include a `description` field for tools.
    *   Updated the API to handle the new `description` field.
    *   Updated the agent service to fetch tools from MCP servers.
    *   Updated the API for adding tools to agents.
    *   Implemented logging for monitoring.
    *   Implemented conversation management.
    *   Added API documentation section to `PROJECT_OVERVIEW.md`.