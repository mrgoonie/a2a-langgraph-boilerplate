"""
This module sets up SQLAlchemy relationships between models after they are all defined.
This helps avoid circular dependencies that can cause import errors.
"""

from .crew import Crew
from .agent import Agent
from .conversation import Conversation
from .tool import Tool
from .mcp_server import McpServer

# Set up Crew relationships
Crew.agents = Crew.agents.property.parent.class_attribute.property
Crew.conversations = Crew.conversations.property.parent.class_attribute.property

# Set up Agent relationships
Agent.crew = Agent.crew.property.parent.class_attribute.property
Agent.conversations = Agent.conversations.property.parent.class_attribute.property

# Set up Conversation relationships
Conversation.crew = Conversation.crew.property.parent.class_attribute.property
Conversation.agent = Conversation.agent.property.parent.class_attribute.property

# Set up Tool relationships
Tool.mcp_server = Tool.mcp_server.property.parent.class_attribute.property
