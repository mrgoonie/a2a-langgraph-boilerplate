from fastapi import FastAPI, Request
from app.api import crews, agents, mcp_servers, tools, conversations
from app.models import *
from app.core.logging import get_logger

logger = get_logger(__name__)

app = FastAPI()

@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Request: {request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"Response: {response.status_code}")
    return response

app.include_router(crews.router, prefix="/crews", tags=["crews"])
app.include_router(agents.router, prefix="/agents", tags=["agents"])
app.include_router(mcp_servers.router, prefix="/mcp_servers", tags=["mcp_servers"])
app.include_router(tools.router, prefix="/tools", tags=["tools"])
app.include_router(conversations.router, prefix="/conversations", tags=["conversations"])

@app.get("/")
def read_root():
    return {"message": "Welcome to the Multi AI Agents System Boilerplate"}
