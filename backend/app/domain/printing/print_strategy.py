from typing import Dict, List
from .. import StrategyMeta
from abc import ABC, abstractmethod
from labels import Specification, Sheet
from reportlab.graphics.shapes import Drawing
from reportlab.pdfbase.pdfmetrics import stringWidth
from app.schemas.printing_strategy import PrintingSubjectEnum
from typing import Type


class PrintStrategyBase(ABC, metaclass=StrategyMeta):
    name: str  # name of the strategy
    labelspecs: Specification | None = None  # Add this line for label specs
    draw_border: bool = False
    copies: int = 1
    subjects: List[PrintingSubjectEnum] = [PrintingSubjectEnum.HARDWARE]

    @classmethod
    def create_printing_strategy(
        cls, name: str, *args, **kwargs
    ) -> "PrintStrategyBase":
        for subclass in cls._registry:
            if subclass.name == name:
                return subclass(*args, **kwargs)
        raise ValueError(f"No printing strategy with name '{name}' found.")

    @classmethod
    def clear_registry(cls):
        cls._registry.clear()

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
    return [
        cls.name for cls in PrintStrategyBase._registry if not cls.name.startswith("__")
    ]


def find_print_strategy(name: str) -> Type[PrintStrategyBase] | None:
    for cls in PrintStrategyBase._registry:
        if cls.name == name and not cls.name.startswith("__"):
            return cls
    return None


def get_strategy_subjects(name: str) -> List[PrintingSubjectEnum]:
    strategy_cls = find_print_strategy(name)
    if strategy_cls is None:
        return []

    subjects = getattr(strategy_cls, "subjects", []) or []
    normalized_subjects: List[PrintingSubjectEnum] = []
    for subject in subjects:
        try:
            normalized_subjects.append(
                subject if isinstance(subject, PrintingSubjectEnum) else PrintingSubjectEnum(subject)
            )
        except ValueError:
            continue
    return normalized_subjects
