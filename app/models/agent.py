from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base
from .agent_tool import agent_tool

class Agent(Base):
    __tablename__ = "agents"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    role = Column(String)
    system_prompt = Column(Text)
    crew_id = Column(Integer, ForeignKey("crews.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    crew = relationship("Crew", back_populates="agents")
    tools = relationship("Tool", secondary=agent_tool, back_populates="agents")
    conversations = relationship("Conversation", back_populates="agent")
