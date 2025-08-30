from typing import List
from pydantic import BaseModel


class PartsboxItemBase(BaseModel):
    """
    Schema for API response models based on the PartsboxItem model.
    """

    id: str
    name: str
    description: str
    total_stock: int
    storage_place: str
    material_part_number: str
    queued_for_printing: bool = False

    class ConfigDict:
        from_attributes = True


class PartsBoxItemPage(BaseModel):
    items: List[PartsboxItemBase]
    total: int
