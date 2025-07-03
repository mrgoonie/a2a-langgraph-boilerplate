from pydantic import BaseModel, UUID4
from typing import List, Optional

class AgentBase(BaseModel):
    name: str
    crew_id: UUID4
    role: str
    system_prompt: str

class AgentCreate(AgentBase):
    tools: Optional[List[UUID4]] = []

class Agent(AgentBase):
    id: UUID4

    class Config:
        from_attributes = True
