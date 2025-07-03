from pydantic import BaseModel, UUID4

class ToolBase(BaseModel):
    name: str
    description: str
    mcp_server_id: UUID4

class ToolCreate(ToolBase):
    pass

class Tool(ToolBase):
    id: UUID4

    class Config:
        from_attributes = True
