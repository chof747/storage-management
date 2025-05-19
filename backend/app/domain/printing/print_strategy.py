from app.models.hardware_item import HardwareItem
from .. import StrategyMeta
from abc import ABC, abstractmethod


class PrintStrategyBase(ABC, metaclass=StrategyMeta):
    name: str  # name of the strategy

    @abstractmethod
    def __call__(self, item: HardwareItem) -> str:
        pass


def get_all_printing_strategies() -> list[str]:
    return [cls.name for cls in PrintStrategyBase._registry]


# Default strategies
class GridfinityPrinter(PrintStrategyBase):
    name = "Gridfinity"

    def __call__(self, item: HardwareItem):
        return "to be implemented"


class StorageBoxPrinter(PrintStrategyBase):
    name = "Storage Box"

    def __call__(self, item: HardwareItem):
        return "to be implemented"
