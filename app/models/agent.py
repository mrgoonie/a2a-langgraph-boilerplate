from sqlalchemy import Column, String, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from .base import Base, GUID, generate_uuid

class Agent(Base):
    __tablename__ = "agents"

    id = Column(GUID, primary_key=True, index=True, default=generate_uuid)
    name = Column(String, index=True)
    role = Column(String)
    system_prompt = Column(Text)
    crew_id = Column(GUID, ForeignKey("crews.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships are defined in setup_relationships.py to avoid circular dependencies
    pass
