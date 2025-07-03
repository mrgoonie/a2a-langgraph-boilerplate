"""
This module handles late-binding relationship setup for SQLAlchemy models.
It imports and configures relationships after all model classes have been defined,
avoiding circular dependency issues.
"""

from sqlalchemy.orm import relationship
from .agent import Agent
from .crew import Crew
from .conversation import Conversation
from .tool import Tool
from .mcp_server import McpServer
from .agent_tool import agent_tool

# Define relationships here after all models have been fully defined
def setup_relationships():
    """
    Set up relationships between models after they're all defined.
    This resolves circular dependency issues.
    """
    # Add Crew relationships
    Crew.agents = relationship("Agent", back_populates="crew")
    Crew.conversations = relationship("Conversation", back_populates="crew", lazy="dynamic")
    
    # Add Agent relationships
    Agent.crew = relationship("Crew", back_populates="agents")
    Agent.conversations = relationship("Conversation", back_populates="agent", lazy="dynamic")
    Agent.tools = relationship("Tool", secondary=agent_tool, back_populates="agents")
    
    # Add Conversation relationships
    Conversation.crew = relationship("Crew", back_populates="conversations")
    Conversation.agent = relationship("Agent", back_populates="conversations")
    
    # Add Tool relationships
    Tool.agents = relationship("Agent", secondary=agent_tool, back_populates="tools")
    Tool.mcp_server = relationship("McpServer", back_populates="tools")
    
    # Add McpServer relationships
    McpServer.tools = relationship("Tool", back_populates="mcp_server")
