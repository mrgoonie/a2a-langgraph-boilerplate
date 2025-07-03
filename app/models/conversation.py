from sqlalchemy import Column, String, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from .base import Base, GUID, generate_uuid

class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(GUID, primary_key=True, index=True, default=generate_uuid)
    crew_id = Column(GUID, ForeignKey("crews.id"))
    agent_id = Column(GUID, ForeignKey("agents.id"))
    user_input = Column(Text)
    agent_output = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships are defined in setup_relationships.py to avoid circular dependencies
    pass
