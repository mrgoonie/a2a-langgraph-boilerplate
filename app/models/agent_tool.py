from sqlalchemy import Column, Integer, ForeignKey, Table
from .base import Base

agent_tool = Table(
    "agent_tool",
    Base.metadata,
    Column("agent_id", Integer, ForeignKey("agents.id"), primary_key=True),
    Column("tool_id", Integer, ForeignKey("tools.id"), primary_key=True),
)
