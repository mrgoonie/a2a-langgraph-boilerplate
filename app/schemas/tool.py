from pydantic import BaseModel

class ToolBase(BaseModel):
    name: str
    description: str
    mcp_server_id: int

class ToolCreate(ToolBase):
    pass

class Tool(ToolBase):
    id: int

    class Config:
        from_attributes = True
