from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
from app.core.database import get_db
from app.services import mcp_server as mcp_server_service
from app.schemas import mcp_server as mcp_server_schema

router = APIRouter()

@router.post("/", response_model=mcp_server_schema.McpServer)
def create_mcp_server(mcp_server: mcp_server_schema.McpServerCreate, db: Session = Depends(get_db)):
    return mcp_server_service.create_mcp_server(db=db, mcp_server=mcp_server)

@router.get("/", response_model=list[mcp_server_schema.McpServer])
def read_mcp_servers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    mcp_servers = mcp_server_service.get_mcp_servers(db, skip=skip, limit=limit)
    return mcp_servers

@router.get("/{mcp_server_id}", response_model=mcp_server_schema.McpServer)
def read_mcp_server(mcp_server_id: UUID, db: Session = Depends(get_db)):
    db_mcp_server = mcp_server_service.get_mcp_server(db, mcp_server_id=mcp_server_id)
    if db_mcp_server is None:
        raise HTTPException(status_code=404, detail="MCP Server not found")
    return db_mcp_server

@router.put("/{mcp_server_id}", response_model=mcp_server_schema.McpServer)
def update_mcp_server(mcp_server_id: UUID, mcp_server: mcp_server_schema.McpServerCreate, db: Session = Depends(get_db)):
    return mcp_server_service.update_mcp_server(db=db, mcp_server_id=mcp_server_id, mcp_server=mcp_server)

@router.delete("/{mcp_server_id}", response_model=mcp_server_schema.McpServer)
def delete_mcp_server(mcp_server_id: UUID, db: Session = Depends(get_db)):
    return mcp_server_service.delete_mcp_server(db=db, mcp_server_id=mcp_server_id)

@router.get("/{mcp_server_id}/tools")
async def get_mcp_server_tools(mcp_server_id: UUID, db: Session = Depends(get_db)):
    return await mcp_server_service.get_mcp_server_tools(db=db, mcp_server_id=mcp_server_id)

@router.get("/{mcp_server_id}/resources")
async def get_mcp_server_resources(mcp_server_id: UUID, db: Session = Depends(get_db)):
    return await mcp_server_service.get_mcp_server_resources(db=db, mcp_server_id=mcp_server_id)

@router.get("/{mcp_server_id}/prompts")
async def get_mcp_server_prompts(mcp_server_id: UUID, db: Session = Depends(get_db)):
    return await mcp_server_service.get_mcp_server_prompts(db=db, mcp_server_id=mcp_server_id)
