from typing import Dict
from .. import StrategyMeta
from abc import ABC, abstractmethod
from labels import Specification, Sheet
from reportlab.graphics.shapes import Drawing


class PrintStrategyBase(ABC, metaclass=StrategyMeta):
    name: str  # name of the strategy
    labelspecs: Specification | None = None  # Add this line for label specs
    draw_border: bool = False

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
    def draw_label(self, label: Drawing, width: int, height: int, item: Dict[str, str]):
        pass


def get_all_printing_strategies() -> list[str]:
    return [cls.name for cls in PrintStrategyBase._registry]
