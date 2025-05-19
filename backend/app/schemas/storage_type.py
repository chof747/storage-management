from pydantic import BaseModel, ConfigDict, Field, field_validator
from typing import List, Optional

from app.domain.printing.print_strategy import get_all_printing_strategies


class StorageTypeBase(BaseModel):
    name: str = Field(..., max_length=80, description="Name of the Element")
    printing_strategy: str = Field(..., max_length=80, description="Label Printer")
    description: Optional[str] = Field(
        None, description="Description of the storage type"
    )

    @field_validator("printing_strategy")
    def must_be_a_valid_printing_strategy(cls, v):
        printers: List[str] = get_all_printing_strategies()
        if v not in printers:
            raise ValueError(
                f"""Invalid label printer specified: {v}, use any of: '{"', '".join(printers)}'"""
            )
        return v


class StorageTypeCreate(StorageTypeBase):
    pass


class StorageTypeUpdate(StorageTypeBase):
    pass


class StorageTypeInDB(StorageTypeBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class StorageTypePage(BaseModel):
    items: List[StorageTypeInDB]
    total: int
