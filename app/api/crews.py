from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services import crew as crew_service
from app.schemas import crew as crew_schema
from app.schemas import prompt as prompt_schema

router = APIRouter()

@router.post("/", response_model=crew_schema.Crew)
def create_crew(crew: crew_schema.CrewCreate, db: Session = Depends(get_db)):
    return crew_service.create_crew(db=db, crew=crew)

@router.get("/", response_model=list[crew_schema.Crew])
def read_crews(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    crews = crew_service.get_crews(db, skip=skip, limit=limit)
    return crews

@router.get("/{crew_id}", response_model=crew_schema.Crew)
def read_crew(crew_id: int, db: Session = Depends(get_db)):
    db_crew = crew_service.get_crew(db, crew_id=crew_id)
    if db_crew is None:
        raise HTTPException(status_code=404, detail="Crew not found")
    return db_crew

@router.put("/{crew_id}", response_model=crew_schema.Crew)
def update_crew(crew_id: int, crew: crew_schema.CrewCreate, db: Session = Depends(get_db)):
    return crew_service.update_crew(db=db, crew_id=crew_id, crew=crew)

@router.delete("/{crew_id}", response_model=crew_schema.Crew)
def delete_crew(crew_id: int, db: Session = Depends(get_db)):
    return crew_service.delete_crew(db=db, crew_id=crew_id)

@router.post("/{crew_id}/execute", response_model=dict)
def execute_prompt(crew_id: int, prompt: prompt_schema.PromptCreate, db: Session = Depends(get_db)):
    return crew_service.execute_prompt(db=db, crew_id=crew_id, prompt=prompt)
