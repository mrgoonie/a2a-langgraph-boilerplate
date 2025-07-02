from sqlalchemy.orm import Session
from app.models.tool import Tool
from app.schemas.tool import ToolCreate

def create_tool(db: Session, tool: ToolCreate):
    db_tool = Tool(name=tool.name, description=tool.description, mcp_server_id=tool.mcp_server_id)
    db.add(db_tool)
    db.commit()
    db.refresh(db_tool)
    return db_tool

def get_tool(db: Session, tool_id: int):
    return db.query(Tool).filter(Tool.id == tool_id).first()

def get_tools(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Tool).offset(skip).limit(limit).all()

def update_tool(db: Session, tool_id: int, tool: ToolCreate):
    db_tool = db.query(Tool).filter(Tool.id == tool_id).first()
    db_tool.name = tool.name
    db_tool.description = tool.description
    db_tool.mcp_server_id = tool.mcp_server_id
    db.commit()
    db.refresh(db_tool)
    return db_tool

def delete_tool(db: Session, tool_id: int):
    db_tool = db.query(Tool).filter(Tool.id == tool_id).first()
    db.delete(db_tool)
    db.commit()
    return db_tool
