from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base
from .agent_tool import agent_tool

class Tool(Base):
    __tablename__ = "tools"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)
    mcp_server_id = Column(Integer, ForeignKey("mcp_servers.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    mcp_server = relationship("McpServer", back_populates="tools")
    agents = relationship("Agent", secondary=agent_tool, back_populates="tools")
