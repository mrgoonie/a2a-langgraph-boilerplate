from pydantic import BaseModel, UUID4

class CrewBase(BaseModel):
    name: str

class CrewCreate(CrewBase):
    pass

class Crew(CrewBase):
    id: UUID4

    class Config:
        from_attributes = True
