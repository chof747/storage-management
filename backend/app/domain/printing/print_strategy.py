from app.models.hardware_item import HardwareItem
from .. import StrategyMeta
from abc import ABC, abstractmethod
from labels import Specification


class PrintStrategyBase(ABC, metaclass=StrategyMeta):
    name: str  # name of the strategy
    labelspecs: Specification | None = None  # Add this line for label specs

    @abstractmethod
    def __call__(self, item: HardwareItem) -> str:
        pass


def get_all_printing_strategies() -> list[str]:
    return [cls.name for cls in PrintStrategyBase._registry]


# Default strategies
class GridfinityPrinter(PrintStrategyBase):
    name = "Gridfinity"
    labelspecs = Specification(
        sheet_width=210,
        sheet_height=297,  # A4 size in mm
        label_width=17.8,
        label_height=10,
        columns=10,
        rows=27,
        corner_radius=2,
    )

    def __call__(self, item: HardwareItem):
        return "to be implemented"


class StorageBoxPrinter(PrintStrategyBase):
    name = "Storage Box"

    def __call__(self, item: HardwareItem):
        return "to be implemented"
