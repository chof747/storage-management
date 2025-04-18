
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from app.types import StrHttpUrl

class StorageElementBase(BaseModel):
    name: str = Field(..., max_length=80, description="Name of the Element")
    location: str = Field(..., max_length=80, description="Location")
    position: str = Field(..., max_length=80, description="Position within the Location")
    storage_type: str = Field(..., description="Type of Storage")
    description: Optional[str] = Field(None, description="Description of the element's content")

class StorageElementCreate(StorageElementBase):
    pass

class StorageElementUpdate(StorageElementBase):
    pass

class StorageElementInDB(StorageElementBase):
    id: int

    class Config:
        orm_mode = True