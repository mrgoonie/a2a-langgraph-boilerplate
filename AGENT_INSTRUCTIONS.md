# AI Agent Cluster API Instructions

This document provides a step-by-step guide on how to create, manage, and interact with AI crews and agents using the provided API.

## Table of Contents

1.  [Crews](#crews)
    *   [Create a Crew with a Supervisor and Agents](#1-create-a-crew-with-a-supervisor-and-agents)
    *   [Get a list of Crews](#2-get-a-list-of-crews)
    *   [Get a specific Crew](#3-get-a-specific-crew)
    *   [Update a Crew](#4-update-a-crew)
    *   [Delete a Crew](#5-delete-a-crew)
    *   [Execute a Prompt in a Crew](#6-execute-a-prompt-in-a-crew)
2.  [Agents](#agents)
    *   [Create an Agent](#1-create-an-agent)
    *   [Get a list of Agents](#2-get-a-list-of-agents)
    *   [Get a specific Agent](#3-get-a-specific-agent)
    *   [Update an Agent](#4-update-an-agent)
    *   [Delete an Agent](#5-delete-an-agent)
    *   [Add a Tool to an Agent](#6-add-a-tool-to-an-agent)
3.  [Conversations](#conversations)
    *   [Create a Conversation](#1-create-a-conversation)
    *   [Get a list of Conversations](#2-get-a-list-of-conversations)
    *   [Get a specific Conversation](#3-get-a-specific-conversation)

---

## Crews

### 1. Create a Crew with a Supervisor and Agents

To create a new crew with a supervisor and multiple agents, you first need to create the crew, then create the agents and assign them to the crew.

#### Step 1: Create the Crew

Send a `POST` request to the `/crews/` endpoint.

**Endpoint:** `POST /crews/`

**Request Body:**

```json
{
  "name": "My New Crew"
}
```

**Example using `curl`:**

```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/crews/' \
  -H 'Content-Type: application/json' \
  -d '{
  "name": "My New Crew"
}'
```

#### Step 2: Create the Supervisor Agent

Send a `POST` request to the `/agents/` endpoint with the `role` set to `"supervisor"`.

**Endpoint:** `POST /agents/`

**Request Body:**

```json
{
  "name": "My Supervisor",
  "crew_id": 1,
  "role": "supervisor",
  "system_prompt": "You are the supervisor. Your job is to route the conversation to the correct agent."
}
```

**Example using `curl`:**

```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/agents/' \
  -H 'Content-Type: application/json' \
  -d '{
  "name": "My Supervisor",
  "crew_id": 1,
  "role": "supervisor",
  "system_prompt": "You are the supervisor. Your job is to route the conversation to the correct agent."
}'
```

#### Step 3: Create the Worker Agents

Send a `POST` request to the `/agents/` endpoint for each worker agent, with the `role` set to `"worker"`.

**Endpoint:** `POST /agents/`

**Request Body:**

```json
{
  "name": "My Worker Agent 1",
  "crew_id": 1,
  "role": "worker",
  "system_prompt": "You are a worker agent. Your job is to use the available tools to answer the user's questions.",
  "tools": [1, 2]
}
```

**Example using `curl`:**

```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/agents/' \
  -H 'Content-Type: application/json' \
  -d '{
  "name": "My Worker Agent 1",
  "crew_id": 1,
  "role": "worker",
  "system_prompt": "You are a worker agent. Your job is to use the available tools to answer the user's questions.",
  "tools": [1, 2]
}'
```

### 2. Get a list of Crews

To get a list of all crews, send a `GET` request to the `/crews/` endpoint.

**Endpoint:** `GET /crews/`

**Example using `curl`:**

```bash
curl -X 'GET' 'http://127.0.0.1:8000/crews/'
```

### 3. Get a specific Crew

To get a specific crew by its ID, send a `GET` request to the `/crews/{crew_id}` endpoint.

**Endpoint:** `GET /crews/{crew_id}`

**Example using `curl`:**

```bash
curl -X 'GET' 'http://127.0.0.1:8000/crews/1'
```

### 4. Update a Crew

To update a crew's information, send a `PUT` request to the `/crews/{crew_id}` endpoint.

**Endpoint:** `PUT /crews/{crew_id}`

**Request Body:**

```json
{
  "name": "My Updated Crew"
}
```

**Example using `curl`:**

```bash
curl -X 'PUT' \
  'http://127.0.0.1:8000/crews/1' \
  -H 'Content-Type: application/json' \
  -d '{
  "name": "My Updated Crew"
}'
```

### 5. Delete a Crew

To delete a crew, send a `DELETE` request to the `/crews/{crew_id}` endpoint.

**Endpoint:** `DELETE /crews/{crew_id}`

**Example using `curl`:**

```bash
curl -X 'DELETE' 'http://127.0.0.1:8000/crews/1'
```

### 6. Execute a Prompt in a Crew

To execute a prompt within a specific crew, send a `POST` request to the `/crews/{crew_id}/execute` endpoint.

**Endpoint:** `POST /crews/{crew_id}/execute`

**Request Body:**

```json
{
  "user_input": "What is the weather in San Francisco?"
}
```

**Example using `curl`:**

```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/crews/1/execute' \
  -H 'Content-Type: application/json' \
  -d '{
  "user_input": "What is the weather in San Francisco?"
}'
```

---

## Agents

### 1. Create an Agent

To create a new agent within a crew, send a `POST` request to the `/agents/` endpoint.

**Endpoint:** `POST /agents/`

**Request Body:**

```json
{
  "name": "My New Agent",
  "crew_id": 1,
  "role": "worker",
  "system_prompt": "You are a worker agent. Your job is to use the available tools to answer the user's questions.",
  "tools": [1, 2]
}
```

**Example using `curl`:**

```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/agents/' \
  -H 'Content-Type: application/json' \
  -d '{
  "name": "My New Agent",
  "crew_id": 1,
  "role": "worker",
  "system_prompt": "You are a worker agent. Your job is to use the available tools to answer the user's questions.",
  "tools": [1, 2]
}'
```

### 2. Get a list of Agents

To get a list of all agents, send a `GET` request to the `/agents/` endpoint.

**Endpoint:** `GET /agents/`

**Example using `curl`:**

```bash
curl -X 'GET' 'http://127.0.0.1:8000/agents/'
```

### 3. Get a specific Agent

To get a specific agent by its ID, send a `GET` request to the `/agents/{agent_id}` endpoint.

**Endpoint:** `GET /agents/{agent_id}`

**Example using `curl`:**

```bash
curl -X 'GET' 'http://127.0.0.1:8000/agents/1'
```

### 4. Update an Agent

To update an agent's information, send a `PUT` request to the `/agents/{agent_id}` endpoint.

**Endpoint:** `PUT /agents/{agent_id}`

**Request Body:

```json
{
  "name": "My Updated Agent",
  "crew_id": 1,
  "role": "worker",
  "system_prompt": "You are a worker agent. Your job is to use the available tools to answer the user's questions.",
  "tools": [1]
}
```

**Example using `curl`:

```bash
curl -X 'PUT' \
  'http://127.0.0.1:8000/agents/1' \
  -H 'Content-Type: application/json' \
  -d '{
  "name": "My Updated Agent",
  "crew_id": 1,
  "role": "worker",
  "system_prompt": "You are a worker agent. Your job is to use the available tools to answer the user's questions.",
  "tools": [1]
}'
```

### 5. Delete an Agent

To delete an agent, send a `DELETE` request to the `/agents/{agent_id}` endpoint.

**Endpoint:** `DELETE /agents/{agent_id}`

**Example using `curl`:**

```bash
curl -X 'DELETE' 'http://127.0.0.1:8000/agents/1'
```

### 6. Add a Tool to an Agent

To add a tool to an agent, send a `POST` request to the `/agents/{agent_id}/tools/{tool_id}` endpoint.

**Endpoint:** `POST /agents/{agent_id}/tools/{tool_id}`

**Example using `curl`:**

```bash
curl -X 'POST' 'http://127.0.0.1:8000/agents/1/tools/3'
```

---

## MCP Servers

### 1. Get a list of available tools of a MCP server

To get a list of available tools of a MCP server, send a `GET` request to the `/mcp_servers/{mcp_server_id}/tools` endpoint.

**Endpoint:** `GET /mcp_servers/{mcp_server_id}/tools`

**Example using `curl`:**

```bash
curl -X 'GET' 'http://127.0.0.1:8000/mcp_servers/1/tools'
```

### 2. Get a list of available resources of a MCP server

To get a list of available resources of a MCP server, send a `GET` request to the `/mcp_servers/{mcp_server_id}/resources` endpoint.

**Endpoint:** `GET /mcp_servers/{mcp_server_id}/resources`

**Example using `curl`:**

```bash
curl -X 'GET' 'http://127.0.0.1:8000/mcp_servers/1/resources'
```

### 3. Get a list of available prompts of a MCP server

To get a list of available prompts of a MCP server, send a `GET` request to the `/mcp_servers/{mcp_server_id}/prompts` endpoint.

**Endpoint:** `GET /mcp_servers/{mcp_server_id}/prompts`

**Example using `curl`:**

```bash
curl -X 'GET' 'http://127.0.0.1:8000/mcp_servers/1/prompts'
```

---

## Conversations

### 1. Create a Conversation

To create a new conversation, send a `POST` request to the `/conversations/` endpoint.

**Endpoint:** `POST /conversations/`

**Request Body:**

```json
{
  "user_input": "Hello, agent!",
  "agent_output": "Hello, user!",
  "crew_id": 1,
  "agent_id": 1
}
```

**Example using `curl`:**

```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/conversations/' \
  -H 'Content-Type: application/json' \
  -d '{
  "user_input": "Hello, agent!",
  "agent_output": "Hello, user!",
  "crew_id": 1,
  "agent_id": 1
}'
```

### 2. Get a list of Conversations

To get a list of all conversations, send a `GET` request to the `/conversations/` endpoint.

**Endpoint:** `GET /conversations/`

**Example using `curl`:**

```bash
curl -X 'GET' 'http://127.0.0.1:8000/conversations/'
```

### 3. Get a specific Conversation

To get a specific conversation by its ID, send a `GET` request to the `/conversations/{conversation_id}` endpoint.

**Endpoint:** `GET /conversations/{conversation_id}`

**Example using `curl`:**

```bash
curl -X 'GET' 'http://127.0.0.1:8000/conversations/1'
```
