from fastapi import FastAPI, Request
from app.api import crews, agents, mcp_servers, tools, conversations
from app.models import *
from app.core.logging import get_logger

logger = get_logger(__name__)

app = FastAPI(
    title="A2A LangGraph Boilerplate API",
    description="""
    A2A (Agent-to-Agent) LangGraph Boilerplate for building AI agent clusters.
    
    ## Authentication
    
    All API endpoints require authentication using an API key. Provide your API key in one of these ways:
    
    1. **Header** (recommended): `X-API-Key: your-api-key`
    2. **Query parameter**: `?api_key=your-api-key`
    
    ## Development
    
    In development mode, you can use the default key: `development-api-key-please-change-in-production`
    
    ## Rate Limiting
    
    API calls are rate-limited to 100 requests per minute per API key.
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

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
    return {
        "message": "Welcome to the Multi AI Agents System Boilerplate",
        "version": "1.0.0",
        "authentication": {
            "required": True,
            "methods": [
                "Header: X-API-Key",
                "Query parameter: api_key"
            ],
            "development_key": "development-api-key-please-change-in-production"
        },
        "docs": {
            "swagger": "/docs",
            "redoc": "/redoc"
        }
    }
