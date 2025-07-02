from pydantic import BaseModel

class McpServerBase(BaseModel):
    name: str
    url: str

class McpServerCreate(McpServerBase):
    pass

class McpServer(McpServerBase):
    id: int

    class Config:
        from_attributes = True
