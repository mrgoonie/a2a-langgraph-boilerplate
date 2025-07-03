from pydantic import BaseModel, UUID4
from typing import List, Optional

class AgentBase(BaseModel):
    name: str
    crew_id: UUID4
    role: str
    system_prompt: str
    model: Optional[str] = None  # OpenRouter model identifier, e.g., 'anthropic/claude-3-opus-20240229'

class AgentCreate(AgentBase):
    tools: Optional[List[UUID4]] = []

class Agent(AgentBase):
    id: UUID4

    class Config:
        from_attributes = True
