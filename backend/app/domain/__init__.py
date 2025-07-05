from abc import ABCMeta


class StrategyMeta(ABCMeta):
    def __init__(cls, name, bases, clsdict):
        if not hasattr(cls, "_registry"):
            cls._registry = set()
        else:
            cls._registry.add(cls)

        super().__init__(name, bases, clsdict)
