from pydantic import BaseModel
from typing import Optional

class ConversationBase(BaseModel):
    user_input: str
    agent_output: str
    crew_id: Optional[int] = None
    agent_id: Optional[int] = None

class ConversationCreate(ConversationBase):
    pass

class Conversation(ConversationBase):
    id: int

    class Config:
        from_attributes = True
