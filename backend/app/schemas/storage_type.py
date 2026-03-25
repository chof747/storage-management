from pydantic import BaseModel, ConfigDict, Field, field_validator
from typing import Dict, List, Optional

from app.domain.printing.print_strategy import (
    get_all_printing_strategies,
    get_strategy_subjects,
)
from app.schemas.printing_strategy import PrintingSubjectEnum


class StorageTypeBase(BaseModel):
    name: str = Field(..., max_length=80, description="Name of the Element")
    printing_strategies: Dict[PrintingSubjectEnum, str] = Field(
        default_factory=dict,
        description="Label printers per subject",
    )
    description: Optional[str] = Field(
        None, description="Description of the storage type"
    )

    @field_validator("printing_strategies")
    def must_be_valid_printing_strategies(cls, v: Dict[PrintingSubjectEnum, str]):
        v = v or {}
        printers: List[str] = get_all_printing_strategies()
        invalid = [strategy for strategy in v.values() if strategy not in printers]
        if invalid:
            available = '", "'.join(printers)
            raise ValueError(
                f'Invalid label printer specified: {", ".join(invalid)}, use any of: "{available}" or leave empty'
            )

        for subject, strategy in v.items():
            supported_subjects = get_strategy_subjects(strategy)
            if supported_subjects and subject not in supported_subjects:
                allowed = '", "'.join(s.value for s in supported_subjects)
                raise ValueError(
                    f'Strategy "{strategy}" cannot print subject "{subject.value}". Supported subjects: "{allowed}"'
                )
        return v


class StorageTypeCreate(StorageTypeBase):
    pass


class StorageTypeUpdate(StorageTypeBase):
    name: Optional[str] = None
    printing_strategies: Optional[Dict[PrintingSubjectEnum, str]] = None
    description: Optional[str] = None


class StorageTypeInDB(StorageTypeBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class StorageTypePage(BaseModel):
    items: List[StorageTypeInDB]
    total: int
