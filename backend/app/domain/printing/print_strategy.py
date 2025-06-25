from typing import Dict
from .. import StrategyMeta
from abc import ABC, abstractmethod
from labels import Specification, Sheet
from reportlab.graphics.shapes import Drawing
from reportlab.pdfbase.pdfmetrics import stringWidth


class PrintStrategyBase(ABC, metaclass=StrategyMeta):
    name: str  # name of the strategy
    labelspecs: Specification | None = None  # Add this line for label specs
    draw_border: bool = False
    copies: int = 1

    @classmethod
    def create_printing_strategy(
        cls, name: str, *args, **kwargs
    ) -> "PrintStrategyBase":
        for subclass in cls._registry:
            if subclass.name == name:
                return subclass(*args, **kwargs)
        raise ValueError(f"No printing strategy with name '{name}' found.")

    def __call__(self, item: Dict[str, str]) -> str:
        pass

    @abstractmethod
    def draw_label(
        self, label: Drawing, width: int, height: int, item: Dict[str, str | None]
    ):
        pass

    def shrink_font_if_needed(
        self,
        text: str,
        start_size: float,
        min_size: float,
        width: float,
        font_name: str,
    ) -> float:
        """Shrinks a text on a label as needed

        This function is shrinking the font size and stops at a minimal font size

        Args:
            text (str): The text to shrink
            start_size (float): the default font size to start with
            min_size (float): the minimal font size to stop at
            margin (int): the margins applied left *and* right of the text
            font_name (str): the name of the font (it must be a registered font)

        Returns:
            float: new font size to apply to fit the text
        """
        font_size = start_size
        print(f'Text = "{text}"')
        print(f"text space = {width}")
        while True:
            print(f"{font_size}")
            text_width = stringWidth(text, font_name, font_size)
            print(f"text width = {text_width}")

            if text_width <= width:
                break
            elif font_size <= min_size:
                return min_size
            else:
                font_size *= 0.8
        return font_size


def get_all_printing_strategies() -> list[str]:
    return [cls.name for cls in PrintStrategyBase._registry]
