from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services import agent as agent_service
from app.schemas import agent as agent_schema

router = APIRouter()

@router.post("/", response_model=agent_schema.Agent)
def create_agent(agent: agent_schema.AgentCreate, db: Session = Depends(get_db)):
    return agent_service.create_agent(db=db, agent=agent)

@router.get("/", response_model=list[agent_schema.Agent])
def read_agents(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    agents = agent_service.get_agents(db, skip=skip, limit=limit)
    return agents

@router.get("/{agent_id}", response_model=agent_schema.Agent)
def read_agent(agent_id: int, db: Session = Depends(get_db)):
    db_agent = agent_service.get_agent(db, agent_id=agent_id)
    if db_agent is None:
        raise HTTPException(status_code=404, detail="Agent not found")
    return db_agent

@router.put("/{agent_id}", response_model=agent_schema.Agent)
def update_agent(agent_id: int, agent: agent_schema.AgentCreate, db: Session = Depends(get_db)):
    return agent_service.update_agent(db=db, agent_id=agent_id, agent=agent)

@router.delete("/{agent_id}", response_model=agent_schema.Agent)
def delete_agent(agent_id: int, db: Session = Depends(get_db)):
    return agent_service.delete_agent(db=db, agent_id=agent_id)

@router.post("/{agent_id}/tools/{tool_id}", response_model=agent_schema.Agent)
def add_tool_to_agent(agent_id: int, tool_id: int, db: Session = Depends(get_db)):
    return agent_service.add_tool_to_agent(db=db, agent_id=agent_id, tool_id=tool_id)
