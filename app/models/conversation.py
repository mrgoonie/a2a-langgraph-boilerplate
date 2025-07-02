from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base

class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    crew_id = Column(Integer, ForeignKey("crews.id"))
    agent_id = Column(Integer, ForeignKey("agents.id"))
    user_input = Column(Text)
    agent_output = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    crew = relationship("Crew", back_populates="conversations")
    agent = relationship("Agent", back_populates="conversations")
