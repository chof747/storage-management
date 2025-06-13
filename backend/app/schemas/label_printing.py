from pydantic import BaseModel
from typing import List


class StartPosition(BaseModel):
    row: int
    col: int


class LabelSheet(BaseModel):
    start_pos: StartPosition


class LabelPrintRequest(BaseModel):
    sheets: List[LabelSheet]
    strategy: str
