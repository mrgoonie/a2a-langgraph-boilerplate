# Conversations Management

This guide covers how to manage conversations between users and AI crews/agents in the A2A LangGraph Boilerplate system.

## What are Conversations?

Conversations represent interactions between users and AI entities (crews or individual agents). Each conversation contains:

- **User Input**: The original query or request from the user
- **Agent Output**: The response from the AI crew or agent
- **Metadata**: Timestamps, associated crew/agent, and execution context
- **Context Tracking**: Maintains conversation history for context-aware responses

## Conversation Architecture

### Components

- **User Interface**: Entry point for user queries
- **Crew Execution**: Processing user input through AI crews
- **Agent Collaboration**: Multi-agent coordination for complex tasks
- **Response Generation**: Synthesis of final responses
- **Storage**: Persistent conversation history

### Conversation Flow

```
User Query → Crew Execution → Agent Processing → Response → Storage
     ↓              ↓              ↓              ↓         ↓
Conversation    Supervisor     Specialized    Synthesis   Database
   Start        Analysis        Agents        Response    Record
```

## Creating Conversations

### Basic Conversation Creation

```python
import requests

conversation_data = {
    "user_input": "Research the latest trends in artificial intelligence",
    "agent_output": "Based on my research, here are the current AI trends...",
    "crew_id": "crew-uuid-here",
    "agent_id": "agent-uuid-here"
}

response = requests.post("http://localhost:8000/conversations/", json=conversation_data)
conversation = response.json()
print(f"Created conversation: {conversation['id']}")
```

### Conversation via Crew Execution

```python
# The recommended way to create conversations is through crew execution
crew_id = "crew-uuid-here"
prompt_data = {
    "content": "Analyze the impact of AI on modern software development"
}

# Execute prompt through crew - this automatically creates a conversation
response = requests.post(f"http://localhost:8000/crews/{crew_id}/execute", json=prompt_data)
result = response.json()

# The conversation is automatically created and stored
print(f"Execution result: {result}")
```

### Conversation with Specific Agent

```python
# For direct agent interaction (less common)
conversation_data = {
    "user_input": "Generate a Python function for data validation",
    "agent_output": "Here's a Python function for data validation...",
    "agent_id": "developer-agent-uuid",
    "crew_id": None  # Can be None for direct agent interaction
}

response = requests.post("http://localhost:8000/conversations/", json=conversation_data)
```

## Conversation Workflow

### End-to-End Example

```python
# 1. Create a crew with specialized agents
crew_data = {
    "name": "Development Team",
    "description": "Full-stack development assistance"
}
crew = requests.post("http://localhost:8000/crews/", json=crew_data).json()

# 2. Add specialized agents to the crew
agents = [
    {
        "name": "Requirements Analyst",
        "role": "analyst",
        "system_instructions": "Analyze and clarify user requirements",
        "crew_id": crew['id']
    },
    {
        "name": "Software Architect", 
        "role": "architect",
        "system_instructions": "Design system architecture and technical solutions",
        "crew_id": crew['id']
    },
    {
        "name": "Code Generator",
        "role": "developer", 
        "system_instructions": "Generate clean, efficient code based on requirements",
        "crew_id": crew['id']
    }
]

for agent_data in agents:
    requests.post("http://localhost:8000/agents/", json=agent_data)

# 3. Execute a complex query through the crew
complex_query = {
    "content": """I need help building a REST API for a task management system.
    
    Requirements:
    - User authentication and authorization
    - CRUD operations for tasks and projects
    - Task assignment and status tracking
    - Due date notifications
    - Data validation and error handling
    
    Please provide a complete solution with code examples."""
}

# 4. Execute and track the conversation
response = requests.post(f"http://localhost:8000/crews/{crew['id']}/execute", json=complex_query)
execution_result = response.json()

print("Conversation completed:")
print(f"- Execution time: {execution_result.get('execution_time', 'N/A')}")
print(f"- Agents involved: {execution_result.get('agents_used', [])}")
print(f"- Final response length: {len(str(execution_result.get('result', '')))}")
```

## Retrieving Conversations

### Get All Conversations

```python
# Retrieve all conversations with pagination
response = requests.get("http://localhost:8000/conversations/?skip=0&limit=50")
conversations = response.json()

print(f"Found {len(conversations)} conversations")
for conv in conversations:
    print(f"- {conv['id']}: {conv['user_input'][:50]}...")
```

### Get Specific Conversation

```python
# Get a specific conversation by ID
conversation_id = "conversation-uuid-here"
response = requests.get(f"http://localhost:8000/conversations/{conversation_id}")
conversation = response.json()

print(f"Conversation: {conversation['id']}")
print(f"User Input: {conversation['user_input']}")
print(f"Agent Output: {conversation['agent_output'][:100]}...")
print(f"Created: {conversation['created_at']}")
```

### Filter Conversations by Crew

```python
# Get conversations for a specific crew
def get_crew_conversations(crew_id):
    response = requests.get("http://localhost:8000/conversations/")
    all_conversations = response.json()
    
    crew_conversations = [
        conv for conv in all_conversations 
        if conv.get('crew_id') == crew_id
    ]
    
    return crew_conversations

crew_conversations = get_crew_conversations("crew-uuid-here")
print(f"Found {len(crew_conversations)} conversations for this crew")
```

### Filter Conversations by Agent

```python
# Get conversations involving a specific agent
def get_agent_conversations(agent_id):
    response = requests.get("http://localhost:8000/conversations/")
    all_conversations = response.json()
    
    agent_conversations = [
        conv for conv in all_conversations 
        if conv.get('agent_id') == agent_id
    ]
    
    return agent_conversations

agent_conversations = get_agent_conversations("agent-uuid-here") 
print(f"Found {len(agent_conversations)} conversations for this agent")
```

## Conversation Analysis

### Conversation Metrics

```python
def analyze_conversations():
    response = requests.get("http://localhost:8000/conversations/")
    conversations = response.json()
    
    metrics = {
        "total_conversations": len(conversations),
        "average_input_length": 0,
        "average_output_length": 0,
        "conversations_by_crew": {},
        "conversations_by_agent": {},
        "recent_conversations": 0
    }
    
    if conversations:
        # Calculate averages
        total_input_len = sum(len(conv['user_input']) for conv in conversations)
        total_output_len = sum(len(conv['agent_output']) for conv in conversations)
        
        metrics["average_input_length"] = total_input_len / len(conversations)
        metrics["average_output_length"] = total_output_len / len(conversations)
        
        # Group by crew
        for conv in conversations:
            crew_id = conv.get('crew_id')
            if crew_id:
                metrics["conversations_by_crew"][crew_id] = \
                    metrics["conversations_by_crew"].get(crew_id, 0) + 1
        
        # Group by agent
        for conv in conversations:
            agent_id = conv.get('agent_id')
            if agent_id:
                metrics["conversations_by_agent"][agent_id] = \
                    metrics["conversations_by_agent"].get(agent_id, 0) + 1
    
    return metrics

# Analyze conversation patterns
metrics = analyze_conversations()
print("Conversation Analysis:")
print(f"- Total conversations: {metrics['total_conversations']}")
print(f"- Average input length: {metrics['average_input_length']:.0f} characters")
print(f"- Average output length: {metrics['average_output_length']:.0f} characters")
print(f"- Active crews: {len(metrics['conversations_by_crew'])}")
print(f"- Active agents: {len(metrics['conversations_by_agent'])}")
```

### Content Analysis

```python
def analyze_conversation_content():
    response = requests.get("http://localhost:8000/conversations/")
    conversations = response.json()
    
    # Common patterns analysis
    input_keywords = {}
    output_patterns = {}
    
    for conv in conversations:
        # Analyze input keywords
        words = conv['user_input'].lower().split()
        for word in words:
            if len(word) > 3:  # Only consider meaningful words
                input_keywords[word] = input_keywords.get(word, 0) + 1
        
        # Analyze output length categories
        output_len = len(conv['agent_output'])
        category = "short" if output_len < 500 else "medium" if output_len < 2000 else "long"
        output_patterns[category] = output_patterns.get(category, 0) + 1
    
    # Get top keywords
    top_keywords = sorted(input_keywords.items(), key=lambda x: x[1], reverse=True)[:10]
    
    return {
        "top_keywords": top_keywords,
        "output_length_distribution": output_patterns
    }

content_analysis = analyze_conversation_content()
print("Content Analysis:")
print("Top keywords:", [f"{word}({count})" for word, count in content_analysis['top_keywords']])
print("Output distribution:", content_analysis['output_length_distribution'])
```

## Conversation Context Management

### Context-Aware Conversations

The system maintains context across conversations through:

1. **Message History**: Previous interactions in the same session
2. **Agent Memory**: Agent-specific context and learning
3. **Crew Knowledge**: Shared context across crew members
4. **User Profiles**: Long-term user interaction patterns

### Context Optimization

```python
# The system includes automatic context management
def manage_conversation_context():
    """
    Context management features:
    - Automatic message summarization for long conversations
    - Context length optimization to prevent token limits
    - Intelligent message prioritization
    - Agent-specific context preservation
    """
    
    context_config = {
        "max_messages": 10,  # Maximum messages to keep in active context
        "summarization_threshold": 5,  # When to start summarizing
        "preserve_critical": True,  # Always keep initial query and final responses
        "agent_memory_limit": 1000  # Max tokens for agent-specific memory
    }
    
    return context_config
```

## Advanced Conversation Features

### Conversation Branching

```python
# Handle complex conversations with multiple paths
def create_branched_conversation(base_conversation_id, branch_query):
    """
    Create a new conversation branch from an existing conversation.
    Useful for exploring alternative solutions or follow-up questions.
    """
    
    # Get the base conversation for context
    base_response = requests.get(f"http://localhost:8000/conversations/{base_conversation_id}")
    base_conversation = base_response.json()
    
    # Create a new conversation with context from the base
    branch_data = {
        "user_input": f"Following up on previous conversation: {branch_query}",
        "agent_output": "",  # Will be filled by execution
        "crew_id": base_conversation.get('crew_id'),
        "agent_id": base_conversation.get('agent_id')
    }
    
    # Execute the branch through the crew
    if base_conversation.get('crew_id'):
        prompt_data = {"content": branch_query}
        response = requests.post(
            f"http://localhost:8000/crews/{base_conversation['crew_id']}/execute",
            json=prompt_data
        )
        return response.json()
    
    return branch_data

# Example: Create a follow-up conversation
followup_result = create_branched_conversation(
    "base-conversation-uuid",
    "Can you provide more details about the authentication implementation?"
)
```

### Conversation Templates

```python
# Common conversation patterns
conversation_templates = {
    "code_review": {
        "user_input_template": "Please review this code: {code}",
        "expected_agents": ["code_reviewer", "security_analyst"],
        "output_format": "structured_feedback"
    },
    
    "research_query": {
        "user_input_template": "Research and analyze: {topic}",
        "expected_agents": ["researcher", "analyst", "summarizer"],
        "output_format": "comprehensive_report"
    },
    
    "problem_solving": {
        "user_input_template": "Help me solve: {problem}",
        "expected_agents": ["analyst", "solution_architect", "implementer"],
        "output_format": "step_by_step_solution"
    }
}

def create_templated_conversation(template_name, **kwargs):
    template = conversation_templates.get(template_name)
    if not template:
        return {"error": "Template not found"}
    
    user_input = template["user_input_template"].format(**kwargs)
    return {"user_input": user_input, "template": template}
```

## Conversation Export and Reporting

### Export Conversations

```python
import json
from datetime import datetime

def export_conversations(format="json", filter_criteria=None):
    """Export conversations for backup or analysis."""
    
    response = requests.get("http://localhost:8000/conversations/")
    conversations = response.json()
    
    # Apply filters if specified
    if filter_criteria:
        if "crew_id" in filter_criteria:
            conversations = [c for c in conversations if c.get("crew_id") == filter_criteria["crew_id"]]
        if "date_range" in filter_criteria:
            # Filter by date range (implementation depends on date format)
            pass
    
    export_data = {
        "export_date": datetime.now().isoformat(),
        "total_conversations": len(conversations),
        "conversations": conversations
    }
    
    if format == "json":
        return json.dumps(export_data, indent=2)
    elif format == "csv":
        # Convert to CSV format
        import csv
        import io
        
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["ID", "User Input", "Agent Output", "Crew ID", "Agent ID", "Created At"])
        
        for conv in conversations:
            writer.writerow([
                conv["id"],
                conv["user_input"][:100] + "..." if len(conv["user_input"]) > 100 else conv["user_input"],
                conv["agent_output"][:100] + "..." if len(conv["agent_output"]) > 100 else conv["agent_output"],
                conv.get("crew_id", ""),
                conv.get("agent_id", ""),
                conv.get("created_at", "")
            ])
        
        return output.getvalue()
    
    return export_data

# Export all conversations as JSON
json_export = export_conversations("json")
print("Conversations exported as JSON")

# Export crew-specific conversations as CSV
csv_export = export_conversations("csv", {"crew_id": "specific-crew-uuid"})
print("Crew conversations exported as CSV")
```

### Conversation Reports

```python
def generate_conversation_report():
    """Generate a comprehensive conversation report."""
    
    response = requests.get("http://localhost:8000/conversations/")
    conversations = response.json()
    
    report = {
        "summary": {
            "total_conversations": len(conversations),
            "date_range": "last_30_days",  # Implement date filtering
            "most_active_crew": None,
            "most_active_agent": None
        },
        "metrics": {
            "average_response_time": "2.5s",  # From logs
            "success_rate": "95%",  # From execution results
            "user_satisfaction": "4.2/5"  # From feedback if available
        },
        "trends": {
            "conversation_growth": "+15%",
            "popular_topics": ["AI development", "API design", "data analysis"],
            "peak_hours": ["9-11 AM", "2-4 PM"]
        }
    }
    
    return report

# Generate and display report
report = generate_conversation_report()
print("Conversation Report:")
print(f"- Total conversations: {report['summary']['total_conversations']}")
print(f"- Average response time: {report['metrics']['average_response_time']}")
print(f"- Success rate: {report['metrics']['success_rate']}")
```

## Best Practices

### Conversation Design

1. **Clear Queries**: Encourage users to provide clear, specific queries
2. **Context Preservation**: Maintain relevant context across interactions
3. **Progressive Disclosure**: Break complex queries into manageable parts
4. **Error Recovery**: Handle failed conversations gracefully

### Performance Optimization

1. **Context Management**: Optimize context length for better performance
2. **Caching**: Cache frequently accessed conversations
3. **Async Processing**: Use asynchronous processing for long conversations
4. **Resource Management**: Monitor and manage resource usage

### Quality Assurance

1. **Response Validation**: Validate agent responses for quality
2. **Feedback Collection**: Gather user feedback on conversation quality
3. **Continuous Improvement**: Use conversation data to improve agents
4. **Error Monitoring**: Track and analyze conversation failures

### Privacy and Security

1. **Data Protection**: Ensure conversation data is properly protected
2. **Access Control**: Implement appropriate access controls
3. **Data Retention**: Define and implement data retention policies
4. **Audit Logging**: Maintain audit logs for compliance

This comprehensive approach to conversation management ensures effective tracking, analysis, and optimization of user interactions with your AI agent system.