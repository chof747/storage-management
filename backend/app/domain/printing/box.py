from typing import Dict
from .print_strategy import PrintStrategyBase
from labels import Specification
from reportlab.graphics.shapes import Drawing


class StorageBoxPrinter(PrintStrategyBase):
    """Storage Box printing strategy

    Uses Avery format: Avery_Zweckform_105x74-R

    """

    name = "Storage Box"
    labelspecs = Specification(
        sheet_width=210,
        sheet_height=297,  # A4 size in mm
        label_width=105,
        label_height=74,
        columns=2,
        rows=4,
        corner_radius=0,
    )

    def draw_label(self, label: Drawing, width: int, height: int, item: Dict[str, str]):
        pass
