from sqlalchemy import Column, String, DateTime
from sqlalchemy.sql import func
from .base import Base, GUID, generate_uuid

class McpServer(Base):
    __tablename__ = "mcp_servers"

    id = Column(GUID, primary_key=True, index=True, default=generate_uuid)
    name = Column(String, index=True)
    url = Column(String, unique=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships are defined in setup_relationships.py to avoid circular dependencies
    pass
