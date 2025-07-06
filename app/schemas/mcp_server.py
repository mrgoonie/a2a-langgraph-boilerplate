from pydantic import BaseModel, UUID4, ConfigDict

class McpServerBase(BaseModel):
    name: str
    url: str

class McpServerCreate(McpServerBase):
    pass

class McpServer(McpServerBase):
    id: UUID4

    model_config = ConfigDict(from_attributes=True)
