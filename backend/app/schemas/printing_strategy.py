from typing import List
from pydantic import BaseModel


class LabelSpecification(BaseModel):
    sheet_width: float
    sheet_height: float
    label_width: float
    label_height: float
    columns: int
    rows: int
    left_margin: float
    top_margin: float
    corner_radius: float
    row_gap: float
    column_gap: float


class LabelFont(BaseModel):
    family: str
    size: int
    min_size: int


class LabelMargins(BaseModel):
    top_margin: float
    bottom_margin: float
    left_margin: float
    right_margin: float


class LabelContent(BaseModel):
    template: str
    draw_border: bool
    resize_font: List[bool]


class Finish(BaseModel):
    copies: int


class PrintingStrategyDefinition(BaseModel):
    name: str
    label_specification: LabelSpecification
    label_font: LabelFont
    label_margins: LabelMargins
    label_content: LabelContent
    finish: Finish
