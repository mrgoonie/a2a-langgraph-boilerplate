from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from .base import Base, GUID, generate_uuid

class Tool(Base):
    __tablename__ = "tools"

    id = Column(GUID, primary_key=True, index=True, default=generate_uuid)
    name = Column(String, index=True)
    description = Column(String)
    mcp_server_id = Column(GUID, ForeignKey("mcp_servers.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships are defined in setup_relationships.py to avoid circular dependencies
    pass
