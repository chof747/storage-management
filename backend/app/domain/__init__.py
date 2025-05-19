from abc import ABCMeta


class StrategyMeta(ABCMeta):
    def __init__(cls, name, bases, clsdict):
        if not hasattr(cls, "_registry"):
            cls._registry = []
        else:
            cls._registry.append(cls)

        super().__init__(name, bases, clsdict)
