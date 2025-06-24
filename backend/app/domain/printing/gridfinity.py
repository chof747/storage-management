from typing import Dict, Tuple
from .print_strategy import PrintStrategyBase
from labels import Specification
from reportlab.graphics.shapes import Drawing
from reportlab.graphics import shapes
from jinja2 import Environment

j2env = Environment()
LABEL_TEMPLATE = j2env.from_string(
    """{{ item.main_metric }}/{{ item.secondary_metric|default('') }}
{{ item.length }}"""
)


class GridfinityPrinter(PrintStrategyBase):
    """Gridfinity printing strategy

    Uses Avery format: L4730REV-25

    """

    name = "Gridfinity"
    labelspecs = Specification(
        sheet_width=210,
        sheet_height=297,  # A4 size in mm
        label_width=17.8,
        label_height=10,
        columns=10,
        rows=27,
        left_margin=5,
        top_margin=14,
        corner_radius=2,
        row_gap=0,
        column_gap=2,
    )

    draw_border = False
    copies = 2

    font_size = 12
    min_font_size = 8
    top_margin = 2
    bottom_margin = 3
    left_margin = 2
    font_name = "Helvetica"

    def compile_lines(self, item: Dict[str, str]) -> Tuple[str, str]:
        text = LABEL_TEMPLATE.render(item=item)
        (line1, line2) = text.split("\n")
        return line1, line2

    def draw_label(self, label: Drawing, width: int, height: int, item: Dict[str, str]):

        line1, line2 = self.compile_lines(item)

        font_size = self.shrink_font_if_needed(
            line1, self.font_size, self.min_font_size, width, self.font_name
        )
        label.add(
            shapes.String(
                self.left_margin,
                height - self.font_size - self.top_margin,
                line1,
                fontName=self.font_name,
                fontSize=font_size,
            )
        )

        label.add(
            shapes.String(
                self.left_margin,
                self.bottom_margin,
                line2,
                fontName="Helvetica",
                fontSize=self.font_size,
            )
        )
