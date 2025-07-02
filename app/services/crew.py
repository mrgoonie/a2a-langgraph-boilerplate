from sqlalchemy.orm import Session
from app.models.crew import Crew
from app.models.agent import Agent
from app.schemas.crew import CrewCreate
from app.schemas.prompt import PromptCreate
from app.core.agents import create_agent, create_supervisor
from app.core.graph import AgentGraph
from app.core.tools import create_tavily_tool
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv
import os

load_dotenv()

llm = ChatOpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
    model="anthropic/claude-3-haiku",
)

def create_crew(db: Session, crew: CrewCreate):
    db_crew = Crew(name=crew.name)
    db.add(db_crew)
    db.commit()
    db.refresh(db_crew)
    return db_crew

def get_crew(db: Session, crew_id: int):
    return db.query(Crew).filter(Crew.id == crew_id).first()

def get_crews(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Crew).offset(skip).limit(limit).all()

def update_crew(db: Session, crew_id: int, crew: CrewCreate):
    db_crew = db.query(Crew).filter(Crew.id == crew_id).first()
    db_crew.name = crew.name
    db.commit()
    db.refresh(db_crew)
    return db_crew

def delete_crew(db: Session, crew_id: int):
    db_crew = db.query(Crew).filter(Crew.id == crew_id).first()
    db.delete(db_crew)
    db.commit()
    return db_crew

def execute_prompt(db: Session, crew_id: int, prompt: PromptCreate):
    crew = get_crew(db, crew_id)
    if not crew:
        return {"error": "Crew not found"}
    
    supervisor_model = db.query(Agent).filter(Agent.crew_id == crew_id, Agent.role == "supervisor").first()
    if not supervisor_model:
        return {"error": "Supervisor not found for this crew"}

    agents_data = []
    tools = [create_tavily_tool()]
    for agent_model in crew.agents:
        if agent_model.role != "supervisor":
            agent = create_agent(llm, tools, agent_model.system_prompt)
            agents_data.append({"name": agent_model.name, "agent": agent})

    supervisor = create_supervisor(
        llm,
        agents_data,
        supervisor_model.system_prompt,
    )

    graph = AgentGraph(supervisor, agents_data, tools)
    app = graph.compile()

    result = app.invoke(
        {"messages": [HumanMessage(content=prompt.prompt)]}
    )

    return result

