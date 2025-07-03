from sqlalchemy import Column, ForeignKey, Table
from .base import Base, GUID

agent_tool = Table(
    "agent_tool",
    Base.metadata,
    Column("agent_id", GUID, ForeignKey("agents.id"), primary_key=True),
    Column("tool_id", GUID, ForeignKey("tools.id"), primary_key=True),
)
