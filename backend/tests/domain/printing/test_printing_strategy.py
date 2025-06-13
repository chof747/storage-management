import pytest

from app.domain.printing import get_all_printing_strategies, PrintStrategyBase


def test_get_default_printing_strategies():
    strategies = get_all_printing_strategies()

    assert "Gridfinity" in strategies
    assert "Storage Box" in strategies


def test_get_new_printing_strategy():
    from .new_printing_strategy import TestPrintingStrategy

    ts = TestPrintingStrategy

    strategies = get_all_printing_strategies()
    assert ts.name in strategies


def test_default_border():
    strategy = PrintStrategyBase.create_printing_strategy("Gridfinity")
    assert False == strategy.draw_border

    from .new_printing_strategy import TestPrintingStrategy

    strategy = PrintStrategyBase.create_printing_strategy("Test Strategy")
    assert strategy.draw_border
