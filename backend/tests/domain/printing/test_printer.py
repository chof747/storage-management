from pathlib import Path
from pytest import raises, fixture
from app.domain.printing import Printer, LabelSheet, PrintStrategyBase
from io import BytesIO
from tests.utils.pdf_test_utils import pdf_text


@fixture
def simple_items():
    return [{"phase": "uat", "tester": "Marcus"}, {"phase": "sit", "tester": "Peter"}]


def test_printer_add_items(simple_items):

    strategy = PrintStrategyBase.create_printing_strategy("Gridfinity")
    sheet = LabelSheet(1, strategy.labelspecs)

    printer = Printer(strategy, [sheet])

    added = printer.add(simple_items)
    assert 2 == added


def test_printer_add_too_many_items(simple_items):

    strategy = PrintStrategyBase.create_printing_strategy("Storage Box")
    printer = Printer(strategy)

    with raises(IndexError):
        printer.add(simple_items)

    simple_items.append({"phase": "sit", "tester": "Josef"})

    sheets = [LabelSheet(1, strategy.labelspecs), LabelSheet(2, strategy.labelspecs)]
    sheets[0].start_at(4, 2)
    sheets[1].start_at(4, 2)
    printer = Printer(strategy, sheets)
    with raises(IndexError):
        printer.add(simple_items)


def test_printer_print_basic(simple_items, pdf_text):
    from .new_printing_strategy import TestPrintingStrategy

    strategy = PrintStrategyBase.create_printing_strategy("Test Strategy")
    printer = Printer(
        strategy,
        [
            LabelSheet(1, strategy.labelspecs),
        ],
    )
    printer.add(simple_items)

    document: BytesIO = printer.print()
    text = pdf_text(document)
    try:
        assert "uat:" in text
        assert "Marcus" in text
    except AssertionError:
        printer.print(
            (
                Path(__file__).parent.parent.parent.parent.parent
                / "data"
                / "test_results"
                / "test_printer_print_basic.pdf"
            ).as_posix()
        )
        raise
