
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from app.types import StrHttpUrl
from .storage_element import StorageElementInDB

class HardwareItemBase(BaseModel):
    hwtype: str = Field(..., min_length=2, max_length=80, description="Type of hardware")
    main_metric: str = Field(..., min_length=2, max_length=30, description="Main metric")
    secondary_metric: Optional[str] = None
    length: Optional[float] = None
    reorder: Optional[bool] = False
    reorder_link: Optional[StrHttpUrl] = None
    storage_element_id: int = Field(..., description="Link to storage element")

    @field_validator("main_metric")
    def must_start_with_letter(cls, v: str):
        if not v or not v[0].isalpha():
            raise ValueError("Metric one must start with a letter")
        return v

class HardwareItemCreate(HardwareItemBase):
    pass

class HardwareItemUpdate(HardwareItemBase):
    pass

class HardwareItemInDB(HardwareItemBase):
    id: int
    storage_element : StorageElementInDB
    class Config:
        orm_mode = True