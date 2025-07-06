# AI Crews Management

This guide covers how to create, manage, and work with AI crews in the A2A LangGraph Boilerplate.

## What is an AI Crew?

An AI crew is a collection of AI agents that work together to solve complex problems. Each crew has:
- **A supervisor agent** that coordinates tasks and delegates work
- **Multiple specialized agents** that handle specific types of tasks
- **Shared tools and resources** accessible to all agents in the crew
- **Conversation history** that maintains context across interactions

## Crew Architecture

### Supervisor-Agent Model

The system uses a supervisor-agent architecture where:
- **Supervisor**: Orchestrates the workflow, delegates tasks, and synthesizes results
- **Agents**: Specialized workers that perform specific tasks (research, coding, analysis, etc.)
- **Tools**: External capabilities accessible through MCP (Model Context Protocol) servers

### Workflow Process

1. **User submits a prompt** to the crew
2. **Supervisor analyzes** the request and creates a plan
3. **Supervisor delegates** subtasks to appropriate agents
4. **Agents execute** their assigned tasks using available tools
5. **Supervisor synthesizes** results and provides a final response

## Creating AI Crews

### Basic Crew Creation

```python
import requests

# Create a new crew
crew_data = {
    "name": "Research Team",
    "description": "A team specialized in research and analysis"
}

response = requests.post("http://localhost:8000/crews/", json=crew_data)
crew = response.json()
print(f"Created crew: {crew['id']}")
```

### Crew with Custom Configuration

```python
# Create a crew with specific settings
crew_data = {
    "name": "Development Team",
    "description": "Full-stack development crew with coding and testing capabilities"
}

response = requests.post("http://localhost:8000/crews/", json=crew_data)
crew = response.json()
```

### Automatic Supervisor Creation

When you create a crew, the system automatically creates a supervisor agent with:
- **Name**: "supervisor"
- **Role**: "supervisor"
- **Default instructions**: Basic coordination and delegation tasks
- **Crew assignment**: Automatically linked to the new crew

## Managing Crew Agents

### Adding Agents to a Crew

```python
# Create specialized agents for the crew
agents = [
    {
        "name": "Research Agent",
        "description": "Specialized in information gathering and analysis",
        "role": "researcher",
        "system_instructions": "You are a research specialist. Focus on finding accurate, relevant information and providing detailed analysis.",
        "crew_id": crew_id
    },
    {
        "name": "Code Agent",
        "description": "Specialized in software development and coding",
        "role": "developer",
        "system_instructions": "You are a software developer. Write clean, efficient code and follow best practices.",
        "crew_id": crew_id
    },
    {
        "name": "Summarizer Agent",
        "description": "Specialized in content summarization",
        "role": "summarizer",
        "system_instructions": "You are a content summarizer. Create concise, accurate summaries of complex information.",
        "crew_id": crew_id
    }
]

# Create each agent
for agent_data in agents:
    response = requests.post("http://localhost:8000/agents/", json=agent_data)
    agent = response.json()
    print(f"Created agent: {agent['name']}")
```

### Agent Specialization

Each agent can be specialized for specific tasks:

#### Research Agent
```python
research_agent = {
    "name": "Research Specialist",
    "role": "researcher",
    "system_instructions": """You are a research specialist with expertise in:
    - Information gathering and verification
    - Data analysis and interpretation
    - Source evaluation and citation
    - Trend identification and reporting
    
    Always provide accurate, well-sourced information.""",
    "crew_id": crew_id
}
```

#### Development Agent
```python
developer_agent = {
    "name": "Full Stack Developer",
    "role": "developer",
    "system_instructions": """You are a full-stack developer with expertise in:
    - Frontend and backend development
    - Database design and optimization
    - API development and integration
    - Testing and debugging
    
    Write clean, maintainable code with proper documentation.""",
    "crew_id": crew_id
}
```

#### Analysis Agent
```python
analyst_agent = {
    "name": "Data Analyst",
    "role": "analyst",
    "system_instructions": """You are a data analyst with expertise in:
    - Statistical analysis and modeling
    - Data visualization and reporting
    - Pattern recognition and insights
    - Predictive analytics
    
    Provide clear, actionable insights from data.""",
    "crew_id": crew_id
}
```

## Crew Configuration

### Updating Crew Settings

```python
# Update crew information
update_data = {
    "name": "Advanced Research Team",
    "description": "Enhanced research team with AI and ML capabilities"
}

response = requests.put(f"http://localhost:8000/crews/{crew_id}", json=update_data)
updated_crew = response.json()
```

### Customizing Supervisor Instructions

```python
# Update supervisor agent with custom instructions
supervisor_data = {
    "name": "Team Leader",
    "role": "supervisor",
    "system_instructions": """You are a team leader managing a crew of specialized AI agents.

    Your responsibilities:
    1. Analyze user requests and break them into subtasks
    2. Delegate appropriate tasks to specialized agents
    3. Coordinate between agents and manage workflow
    4. Synthesize results into comprehensive responses
    5. Ensure quality and accuracy of final outputs

    Available agents and their specializations:
    - Research Agent: Information gathering and analysis
    - Code Agent: Software development and technical tasks
    - Summarizer Agent: Content summarization and synthesis

    Always provide clear, actionable responses that address the user's needs.""",
    "crew_id": crew_id
}

response = requests.put(f"http://localhost:8000/agents/{supervisor_id}", json=supervisor_data)
```

## Adding Tools to Crews

### MCP Server Integration

```python
# Create MCP server for tools
mcp_server_data = {
    "name": "Search API",
    "url": "https://searchapi-mcp.prod.diginext.site/mcp",
    "description": "Web search and information retrieval capabilities"
}

response = requests.post("http://localhost:8000/mcp_servers/", json=mcp_server_data)
mcp_server = response.json()
mcp_server_id = mcp_server['id']
```

### Creating Tools

```python
# Create tools for agents
tools = [
    {
        "name": "web_search",
        "description": "Search the web for current information",
        "api_name": "search",
        "mcp_server_id": mcp_server_id
    },
    {
        "name": "code_analysis",
        "description": "Analyze code for quality and best practices",
        "api_name": "analyze_code",
        "mcp_server_id": mcp_server_id
    }
]

# Create each tool
for tool_data in tools:
    response = requests.post("http://localhost:8000/tools/", json=tool_data)
    tool = response.json()
    print(f"Created tool: {tool['name']}")
```

### Assigning Tools to Agents

```python
# Add tools to specific agents
# Research agent gets search capabilities
requests.post(f"http://localhost:8000/agents/{research_agent_id}/tools/{search_tool_id}")

# Developer agent gets code analysis capabilities
requests.post(f"http://localhost:8000/agents/{developer_agent_id}/tools/{code_tool_id}")
```

## Executing Prompts with Crews

### Basic Prompt Execution

```python
# Execute a simple prompt
prompt_data = {
    "content": "Research the latest trends in artificial intelligence and provide a comprehensive summary"
}

response = requests.post(f"http://localhost:8000/crews/{crew_id}/execute", json=prompt_data)
result = response.json()
print(f"Execution result: {result}")
```

### Complex Multi-Agent Tasks

```python
# Complex task requiring multiple agents
complex_prompt = {
    "content": """Please help me with the following project:
    
    1. Research the current state of AI-powered web applications
    2. Analyze the most popular frameworks and technologies
    3. Create a technical specification for a new AI web app
    4. Provide implementation recommendations
    
    I need a comprehensive report with actionable insights."""
}

response = requests.post(f"http://localhost:8000/crews/{crew_id}/execute", json=complex_prompt)
result = response.json()
```

## Monitoring Crew Performance

### Execution Metrics

The system provides execution metrics including:
- **Execution time**: Total time taken for task completion
- **Agent utilization**: Which agents were involved
- **Tool usage**: What tools were accessed
- **Message count**: Number of interactions between agents

### Debugging Workflow Issues

```python
# Check crew configuration
response = requests.get(f"http://localhost:8000/crews/{crew_id}")
crew_details = response.json()

# List all agents in the crew
response = requests.get(f"http://localhost:8000/agents/")
agents = response.json()
crew_agents = [agent for agent in agents if agent['crew_id'] == crew_id]

print(f"Crew has {len(crew_agents)} agents:")
for agent in crew_agents:
    print(f"- {agent['name']} ({agent['role']})")
```

## Best Practices

### Crew Design

1. **Specialized Agents**: Create agents with specific roles and expertise
2. **Clear Instructions**: Provide detailed system instructions for each agent
3. **Appropriate Tools**: Assign relevant tools to agents based on their roles
4. **Balanced Teams**: Include complementary skills in your crew

### Supervisor Configuration

1. **Delegation Strategy**: Configure supervisor to delegate effectively
2. **Quality Control**: Include quality checks in supervisor instructions
3. **Coordination**: Ensure supervisor manages agent interactions properly
4. **Result Synthesis**: Train supervisor to combine results effectively

### Performance Optimization

1. **Task Complexity**: Match task complexity to crew capabilities
2. **Agent Specialization**: Use specialized agents for specific tasks
3. **Tool Efficiency**: Optimize tool usage for performance
4. **Workflow Management**: Monitor and optimize workflow patterns

## Common Use Cases

### Research and Analysis Crew

```python
crew_config = {
    "name": "Research & Analysis Team",
    "agents": [
        {"role": "researcher", "specialization": "information_gathering"},
        {"role": "analyst", "specialization": "data_analysis"},
        {"role": "summarizer", "specialization": "content_synthesis"}
    ],
    "tools": ["web_search", "data_analysis", "document_processing"]
}
```

### Development Crew

```python
crew_config = {
    "name": "Development Team",
    "agents": [
        {"role": "architect", "specialization": "system_design"},
        {"role": "developer", "specialization": "implementation"},
        {"role": "tester", "specialization": "quality_assurance"}
    ],
    "tools": ["code_analysis", "testing_framework", "documentation"]
}
```

### Content Creation Crew

```python
crew_config = {
    "name": "Content Creation Team",
    "agents": [
        {"role": "writer", "specialization": "content_creation"},
        {"role": "editor", "specialization": "content_editing"},
        {"role": "reviewer", "specialization": "quality_review"}
    ],
    "tools": ["content_analysis", "grammar_check", "style_guide"]
}
```

## Error Handling

### Common Issues

1. **Agent Not Found**: Ensure all agents are properly created and assigned
2. **Tool Access Errors**: Verify MCP server connectivity and tool permissions
3. **Workflow Timeouts**: Optimize agent instructions and tool usage
4. **Result Quality**: Review and improve agent specializations

### Troubleshooting Steps

1. **Check Crew Configuration**: Verify all agents and tools are properly set up
2. **Review Logs**: Check server logs for detailed error information
3. **Test Components**: Test individual agents and tools separately
4. **Optimize Instructions**: Improve agent system instructions for better results

## Advanced Features

### Dynamic Agent Management

```python
# Add agents to existing crew dynamically
new_agent = {
    "name": "Specialized Expert",
    "role": "domain_expert",
    "system_instructions": "Custom expertise instructions",
    "crew_id": crew_id
}

response = requests.post("http://localhost:8000/agents/", json=new_agent)
```

### Tool Management

```python
# Update tool configurations
tool_update = {
    "name": "enhanced_search",
    "description": "Enhanced search with AI filtering",
    "api_name": "enhanced_search",
    "mcp_server_id": mcp_server_id
}

response = requests.put(f"http://localhost:8000/tools/{tool_id}", json=tool_update)
```

### Workflow Customization

The system supports customizing workflow patterns through:
- **Agent system instructions**: Define how agents should behave
- **Tool configurations**: Configure how tools should be used
- **Supervisor logic**: Customize coordination and delegation patterns

This flexibility allows you to create highly specialized crews for specific domains and use cases.