from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
from app.core.database import get_db
from app.services import tool as tool_service
from app.schemas import tool as tool_schema

router = APIRouter()

@router.post("/", response_model=tool_schema.Tool)
def create_tool(tool: tool_schema.ToolCreate, db: Session = Depends(get_db)):
    return tool_service.create_tool(db=db, tool=tool)

@router.get("/", response_model=list[tool_schema.Tool])
def read_tools(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    tools = tool_service.get_tools(db, skip=skip, limit=limit)
    return tools

@router.get("/{tool_id}", response_model=tool_schema.Tool)
def read_tool(tool_id: UUID, db: Session = Depends(get_db)):
    db_tool = tool_service.get_tool(db, tool_id=tool_id)
    if db_tool is None:
        raise HTTPException(status_code=404, detail="Tool not found")
    return db_tool

@router.put("/{tool_id}", response_model=tool_schema.Tool)
def update_tool(tool_id: UUID, tool: tool_schema.ToolCreate, db: Session = Depends(get_db)):
    return tool_service.update_tool(db=db, tool_id=tool_id, tool=tool)

@router.delete("/{tool_id}", response_model=tool_schema.Tool)
def delete_tool(tool_id: UUID, db: Session = Depends(get_db)):
    return tool_service.delete_tool(db=db, tool_id=tool_id)
