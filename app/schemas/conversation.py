from pydantic import BaseModel, UUID4, ConfigDict
from typing import Optional

class ConversationBase(BaseModel):
    user_input: str
    agent_output: str
    crew_id: Optional[UUID4] = None
    agent_id: Optional[UUID4] = None

class ConversationCreate(ConversationBase):
    pass

class Conversation(ConversationBase):
    id: UUID4

    model_config = ConfigDict(from_attributes=True)
