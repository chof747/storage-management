from typing import Dict
from app.domain.printing.print_strategy import PrintStrategyBase
from reportlab.graphics.shapes import Drawing
from reportlab.graphics import shapes
from labels import Specification


class TestPrintingStrategy(PrintStrategyBase):
    name = "Test Strategy"
    draw_border = True
    labelspecs = Specification(
        sheet_width=210,
        sheet_height=297,  # A4 size in mm
        label_width=17.8,
        label_height=10,
        columns=10,
        rows=27,
        corner_radius=2,
    )

    def draw_label(
        self, label: Drawing, width: int, height: int, item: Dict[str, str | None]
    ):
        label.add(
            shapes.String(
                2,
                height - 12,
                f"{item['hwtype']}:",
                fontName="Helvetica",
                fontSize=10,
            )
        )

        label.add(
            shapes.String(
                2,
                2,
                f"{item['main_metric']}",
                fontName="Helvetica",
                fontSize=12,
            )
        )
