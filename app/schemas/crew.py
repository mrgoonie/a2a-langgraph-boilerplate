from pydantic import BaseModel, UUID4, ConfigDict

class CrewBase(BaseModel):
    name: str

class CrewCreate(CrewBase):
    pass

class Crew(CrewBase):
    id: UUID4

    model_config = ConfigDict(from_attributes=True)
