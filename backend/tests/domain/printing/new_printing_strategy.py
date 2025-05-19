from app.domain.printing.print_strategy import PrintStrategyBase


class TestPrintingStrategy(PrintStrategyBase):
    name = "Test Strategy"

    def __call__(self, item):
        return "test"
