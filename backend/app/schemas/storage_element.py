from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional

from app.schemas.storage_type import StorageTypeInDB


class StorageElementBase(BaseModel):
    name: str = Field(..., max_length=80, description="Name of the Element")
    location: str = Field(..., max_length=80, description="Location")
    position: str = Field(
        ..., max_length=80, description="Position within the Location"
    )
    storage_type_id: int = Field(..., description="Link to storage type")
    description: Optional[str] = Field(
        None, description="Description of the element's content"
    )


class StorageElementCreate(StorageElementBase):
    pass


class StorageElementUpdate(StorageElementBase):
    pass


class StorageElementInDB(StorageElementBase):
    id: int
    storage_type: StorageTypeInDB

    model_config = ConfigDict(from_attributes=True)


class StorageElementPage(BaseModel):
    items: List[StorageElementInDB]
    total: int
