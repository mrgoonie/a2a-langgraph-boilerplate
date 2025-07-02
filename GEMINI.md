## Overview
This project is a boilerplate for developers who want to start building an AI agent cluster faster and more efficient.

## Concept
* Each AI agent cluster can have multiple AI agent crews (AI Crews)
* Each AI crew can have multiple AI agent, leaded by a superviser (a default AI agent of an AI crew)
* Each AI agent can call tools via MCP servers integration

## How it works
* A supervisor agent will receive input (prompt) from a user via API call, then create a detailed plan with its current capabilities (AI agents underneat and their tools)
* Then request the AI agents to perform tasks via A2A protocol
* Wait for all AI agents finish given tasks
* Grab all the results, analyze and respond to user based on the original input prompt.

## Core Features
* Create & manage AI crews easily (with a default supervisor agent, add/remove AI agents)
* Create & manage AI agents easily (add/remove MCP tools)
* Create & manage MCP servers easily (supports Streamable HTTP transport only)
* Create & manage conversations with AI crews / AI agents easily
* Able to monitor all the activity logs of AI crews and AI agents easily
* Expose API for frontend (nextjs) interaction (support streaming request)
* Expose Swagger API Docs for frontend integration instructions

## Technical Requirements
- Programming language: Python
- Store variables in `.env` file
- AI framework: LangGraph (with OpenRouter AI API)
- Supports Agent-to-Agent (A2A) protocol for AI agents to communicate with each others ("Supervisor" architecture)
- Supports Model Context Protocol (MCP) servers integration (for AI agents to use tool call)
- Expose API for frontend (nextjs) interaction (support streaming request)
- Database: PostgreSQL
- Cloud storage: Cloudflare R2 bucket

## Environment Variables (Development Environment / localhost)

```
DATABASE_URL=""
OPENROUTER_API_KEY=""
...
```

## Documentations & References
* https://langchain-ai.github.io/langgraph/concepts/multi_agent/
* https://github.com/langchain-ai/langgraph
* https://github.com/a2aproject/A2A/tree/main
* https://openrouter.ai/docs/quickstart
* https://www.relari.ai/blog/ai-agent-framework-comparison-langgraph-crewai-openai-swarm
* https://langchain-ai.github.io/langgraph/agents/mcp/
* https://modelcontextprotocol.io/introduction
* https://github.com/modelcontextprotocol/python-sdk

## Instructions
* always store relevent data, application's states, user's states,... in database (PostgreSQL)
* always create/update `PROJECT_OVERVIEW.md` after every task with:
    * project structure (use `tree -L 3 -I 'node_modules|.git|.next'` to generate, then explain the directories briefly)
    * features
    * dependencies
    * api routes
    * todos
    * changelog
* always check `PROJECT_OVERVIEW.md` before starting a new task
* always use `context7` MCP tool to study dependencies/plugins/frameworks' docs carefully while implementing them
* always implement error catching handler
* always implement user-friendly flows
* always follow security best practices
* always commit your code after finishing fixing a bug or implementing a feature completely (DO NOT commit `.env` file)
* always run the development environment in another process and export logs to `./server.log` (view this file to check the logs and debug)