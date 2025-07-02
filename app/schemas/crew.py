from pydantic import BaseModel

class CrewBase(BaseModel):
    name: str

class CrewCreate(CrewBase):
    pass

class Crew(CrewBase):
    id: int

    class Config:
        from_attributes = True
