from sqlalchemy.orm import Session
from uuid import UUID
from app.models.agent import Agent
from app.models.tool import Tool
from app.schemas.agent import AgentCreate
from app.core.tools import create_mcp_tools

def create_agent(db: Session, agent: AgentCreate):
    db_agent = Agent(name=agent.name, crew_id=agent.crew_id, role=agent.role, system_prompt=agent.system_prompt)
    if agent.tools:
        for tool_id in agent.tools:
            tool = db.query(Tool).filter(Tool.id == tool_id).first()
            if tool:
                db_agent.tools.append(tool)
    db.add(db_agent)
    db.commit()
    db.refresh(db_agent)
    return db_agent

def get_agent(db: Session, agent_id: UUID):
    return db.query(Agent).filter(Agent.id == agent_id).first()

def get_agents(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Agent).offset(skip).limit(limit).all()

def update_agent(db: Session, agent_id: UUID, agent: AgentCreate):
    db_agent = db.query(Agent).filter(Agent.id == agent_id).first()
    db_agent.name = agent.name
    db_agent.crew_id = agent.crew_id
    db_agent.role = agent.role
    db_agent.system_prompt = agent.system_prompt
    if agent.tools:
        db_agent.tools = []
        for tool_id in agent.tools:
            tool = db.query(Tool).filter(Tool.id == tool_id).first()
            if tool:
                db_agent.tools.append(tool)
    db.commit()
    db.refresh(db_agent)
    return db_agent

def delete_agent(db: Session, agent_id: UUID):
    db_agent = db.query(Agent).filter(Agent.id == agent_id).first()
    db.delete(db_agent)
    db.commit()
    return db_agent

def add_tool_to_agent(db: Session, agent_id: UUID, tool_id: UUID):
    agent = get_agent(db, agent_id)
    tool = db.query(Tool).filter(Tool.id == tool_id).first()
    if tool.mcp_server_id:
        mcp_server = tool.mcp_server
        mcp_tools = create_mcp_tools(mcp_server.url)
        for mcp_tool in mcp_tools:
            if mcp_tool.name == tool.name:
                agent.tools.append(mcp_tool)
    else:
        agent.tools.append(tool)
    db.commit()
    db.refresh(agent)
    return agent
