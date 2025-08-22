from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from app.types import StrHttpUrl
from .storage_element import StorageElementInDB


class HardwareItemBase(BaseModel):
    hwtype: str = Field(
        ..., min_length=2, max_length=80, description="Type of hardware"
    )
    label: Optional[str] = ""
    main_metric: str = Field(
        ..., min_length=2, max_length=30, description="Main metric"
    )
    secondary_metric: Optional[str] = None
    length: Optional[float] = None
    reorder: Optional[bool] = False
    reorder_link: Optional[StrHttpUrl] = None
    detailed_description: Optional[str] = Field(None, description="Details")
    storage_element_id: int = Field(..., description="Link to storage element")
    queued_for_printing: Optional[bool] = False


class HardwareItemCreate(HardwareItemBase):
    pass


class HardwareItemUpdate(HardwareItemBase):
    hwtype: Optional[str] = None
    label: Optional[str] = None
    main_metric: Optional[str] = None
    secondary_metric: Optional[str] = None
    length: Optional[float] = None
    reorder: Optional[bool] = None
    reorder_link: Optional[str] = None
    detailed_description: Optional[str] = None
    storage_element_id: Optional[int] = None
    queued_for_printing: Optional[bool] = None


class HardwareItemInDB(HardwareItemBase):
    id: int
    storage_element: StorageElementInDB

    model_config = ConfigDict(from_attributes=True)


class HardwareItemPage(BaseModel):
    items: List[HardwareItemInDB]
    total: int


class HardwareItemsMoveRequest(BaseModel):
    storage_to: int
    items: List[int]
