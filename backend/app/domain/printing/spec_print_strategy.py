import os
from typing import Dict, List
from . import PrintStrategyBase
from yaml import safe_load
from labels import Specification
from app.schemas.printing_strategy import PrintingStrategyDefinition
from jinja2 import Template
from reportlab.graphics import shapes


class SpecPrintStrategy(PrintStrategyBase):
    name = "__SpecPrintStrategy"

    def __init_print_strategy(self):
        """Read the parameters from the print strategy"""
        self.labelspecs = Specification(
            **self.__specifications.label_specification.__dict__
        )
        self.draw_border = self.__specifications.label_content.draw_border
        self.copies = self.__specifications.finish.copies
        self.content_template = Template(self.__specifications.label_content.template)

    def __compile_lines(self, item: Dict[str, str | None]) -> List[str]:
        """Generate the lines of the labels based on the provided template"""
        text = self.content_template.render(item=item)
        return text.split("\n")

    def __calc_font_size(self, line: str, l: int, width: float) -> float:
        """Calculate the font size of a line if shrinking is enabled"""
        font_size = self.__specifications.label_font.size
        if (
            len(self.__specifications.label_content.resize_font) >= l
            and self.__specifications.label_content.resize_font[l]
        ):
            font_size = self.shrink_font_if_needed(
                line,
                font_size,
                self.__specifications.label_font.min_size,
                width,
                self.__specifications.label_font.family,
            )
        return font_size

    def __init__(self, spec_data):
        super().__init__()
        self.__specifications = PrintingStrategyDefinition(**spec_data)
        self.__class__.name = self.__specifications.name
        self.__init_print_strategy()

    def draw_label(self, label, width, height, item):
        """Draw the a label for the provided item"""
        lines = self.__compile_lines(item)
        l = 0
        for line in lines:
            font_size = self.__calc_font_size(line, l, width)

            label.add(
                shapes.String(
                    self.__specifications.label_margins.left_margin,
                    height
                    - self.__specifications.label_margins.top_margin
                    - self.__specifications.label_font.line_gap * l
                    - font_size * (l + 1),
                    line,
                    fontName=self.__specifications.label_font.family,
                    fontSize=font_size,
                )
            )
            l = l + 1

    @property
    def specification(self):
        return self.__specifications


def read_spec_from_yml(ymlstream):
    """Read the a yml file with a strategy specification"""
    return safe_load(ymlstream)


def register_yml_strategy(path: str):
    """Register a printing strategy as a subclass of SpecPrintStrategy based on the provided
    specification
    """
    with open(path, "r") as f:
        spec_data = read_spec_from_yml(f)

    strategy_name = spec_data.get("name")
    class_name = strategy_name

    strategy_class = type(
        class_name,
        (SpecPrintStrategy,),
        {
            "name": strategy_name,
            "__module__": __name__,
            "__init__": lambda self: super(
                self.__class__,
                self,
            ).__init__(spec_data),
            # "__init__": lambda self: super().__init__(spec_data),
        },
    )

    globals()[class_name] = strategy_class


def load_strategies(path: str):
    """Load all strategy definition yamls of in a directory and register them as
    printing strategies"""

    if os.path.isdir(path):
        # Load each .yml or .yaml file in the directory
        for entry in sorted(os.listdir(path)):
            full_path = os.path.join(path, entry)
            if os.path.isfile(full_path) and entry.lower().endswith((".yml", ".yaml")):
                register_yml_strategy(full_path)

    elif os.path.isfile(path):
        raise AttributeError(f"Path must be a directory: {path}")

    else:
        raise FileNotFoundError(f"Path does not exist: {path}")
