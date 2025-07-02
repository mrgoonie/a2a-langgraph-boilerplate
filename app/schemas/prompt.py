from pydantic import BaseModel

class PromptBase(BaseModel):
    prompt: str

class PromptCreate(PromptBase):
    pass

class Prompt(PromptBase):
    pass
