import pytest

from app.domain.printing.print_strategy import (
    get_all_printing_strategies,
)


def test_get_default_printing_strategies():
    strategies = get_all_printing_strategies()

    assert "Gridfinity" in strategies
    assert "Storage Box" in strategies


def test_get_new_printing_strategy():
    from .new_printing_strategy import TestPrintingStrategy

    ts = TestPrintingStrategy

    strategies = get_all_printing_strategies()
    assert ts.name in strategies
