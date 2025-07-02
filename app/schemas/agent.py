from pydantic import BaseModel
from typing import List, Optional

class AgentBase(BaseModel):
    name: str
    crew_id: int
    role: str
    system_prompt: str

class AgentCreate(AgentBase):
    tools: Optional[List[int]] = []

class Agent(AgentBase):
    id: int

    class Config:
        from_attributes = True
