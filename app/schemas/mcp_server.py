from pydantic import BaseModel, UUID4

class McpServerBase(BaseModel):
    name: str
    url: str

class McpServerCreate(McpServerBase):
    pass

class McpServer(McpServerBase):
    id: UUID4

    class Config:
        from_attributes = True
