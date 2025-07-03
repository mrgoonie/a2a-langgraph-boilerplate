from sqlalchemy.orm import Session
from uuid import UUID
from app.models.mcp_server import McpServer
from app.schemas.mcp_server import McpServerCreate
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client
from contextlib import AsyncExitStack
from mcp.shared.exceptions import McpError

async def get_mcp_server_tools(db: Session, mcp_server_id: UUID):
    mcp_server = get_mcp_server(db, mcp_server_id)
    if not mcp_server:
        return {"error": "MCP Server not found"}
    
    async with AsyncExitStack() as stack:
        read, write, get_session_id = await stack.enter_async_context(
            streamablehttp_client(url=mcp_server.url)
        )
        async with ClientSession(read, write) as session:
            await session.initialize()
            try:
                tools = await session.list_tools()
                return tools
            except McpError as e:
                if "Method not found" in str(e):
                    return []
                raise e

async def get_mcp_server_resources(db: Session, mcp_server_id: UUID):
    mcp_server = get_mcp_server(db, mcp_server_id)
    if not mcp_server:
        return {"error": "MCP Server not found"}
    
    async with AsyncExitStack() as stack:
        read, write, get_session_id = await stack.enter_async_context(
            streamablehttp_client(url=mcp_server.url)
        )
        async with ClientSession(read, write) as session:
            await session.initialize()
            try:
                resources = await session.list_resources()
                return resources
            except McpError as e:
                if "Method not found" in str(e):
                    return []
                raise e

async def get_mcp_server_prompts(db: Session, mcp_server_id: UUID):
    mcp_server = get_mcp_server(db, mcp_server_id)
    if not mcp_server:
        return {"error": "MCP Server not found"}
    
    async with AsyncExitStack() as stack:
        read, write, get_session_id = await stack.enter_async_context(
            streamablehttp_client(url=mcp_server.url)
        )
        async with ClientSession(read, write) as session:
            await session.initialize()
            try:
                prompts = await session.list_prompts()
                return prompts
            except McpError as e:
                if "Method not found" in str(e):
                    return []
                raise e

def create_mcp_server(db: Session, mcp_server: McpServerCreate):
    db_mcp_server = McpServer(name=mcp_server.name, url=mcp_server.url)
    db.add(db_mcp_server)
    db.commit()
    db.refresh(db_mcp_server)
    return db_mcp_server

def get_mcp_server(db: Session, mcp_server_id: UUID):
    return db.query(McpServer).filter(McpServer.id == mcp_server_id).first()

def get_mcp_servers(db: Session, skip: int = 0, limit: int = 100):
    return db.query(McpServer).offset(skip).limit(limit).all()

def update_mcp_server(db: Session, mcp_server_id: UUID, mcp_server: McpServerCreate):
    db_mcp_server = db.query(McpServer).filter(McpServer.id == mcp_server_id).first()
    db_mcp_server.name = mcp_server.name
    db_mcp_server.url = mcp_server.url
    db.commit()
    db.refresh(db_mcp_server)
    return db_mcp_server

def delete_mcp_server(db: Session, mcp_server_id: UUID):
    db_mcp_server = db.query(McpServer).filter(McpServer.id == mcp_server_id).first()
    db.delete(db_mcp_server)
    db.commit()
    return db_mcp_server
