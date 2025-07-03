from app.core.database import engine
from app.models.base import Base
from app.models.crew import Crew
from app.models.agent import Agent
from app.models.mcp_server import McpServer
from app.models.tool import Tool
from app.models.conversation import Conversation
from app.models.agent_tool import agent_tool

def create_tables():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    create_tables()
