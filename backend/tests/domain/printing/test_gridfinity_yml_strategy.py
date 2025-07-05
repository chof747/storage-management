from pathlib import Path
from pytest import raises, fixture
from app.domain.printing import Printer, LabelSheet, PrintStrategyBase
from io import BytesIO
from tests.utils.pdf_test_utils import pdf_text
from app.models import HardwareItem
from app.schemas.label_printing import LabelSheet as LabelSheetDefinition, StartPosition
from app.domain.printing.spec_print_strategy import register_yml_strategy


@fixture
def load_strategy():
    RESOURCE_PATH = Path(__file__).parent.parent.parent / "resources"
    register_yml_strategy(str(RESOURCE_PATH / "print-strategy-test.yml"))
    return True


def test_gridfinity_yml_printer(db_session, pdf_text, load_strategy):

    sheet_defs = [LabelSheetDefinition(start_pos=StartPosition(row=27, col=7))]
    printer = Printer.create_printer("GridfinityYml", sheet_defs)

    items = db_session.query(HardwareItem).all()
    for i in items:
        i.queued_for_printing = True
    added = printer.add(items)
    assert 2 == added

    document: BytesIO = printer.print()
    text = pdf_text(document)
    try:
        assert 4 == text.count("M3")
        assert 2 == text.count("BH")
        assert 2 == text.count("5.0")
    except AssertionError:
        printer.print(
            (
                Path(__file__).parent.parent.parent.parent.parent
                / "data"
                / "test_results"
                / "test_gridfinity.pdf"
            ).as_posix()
        )
        raise

    # check if
    assert any(not i.queued_for_printing for i in db_session.query(HardwareItem).all())


def test_gridfinity_no_secondary(db_session, pdf_text, load_strategy):

    sheet_defs = [LabelSheetDefinition(start_pos=StartPosition(row=20, col=5))]
    printer = Printer.create_printer("GridfinityYml", sheet_defs)

    item = HardwareItem()
    item.main_metric = "MM"
    item.length = 3
    item.set_for_printing()
    printer.add([item])

    document: BytesIO = printer.print()
    text = pdf_text(document)
    try:
        assert 2 == text.count("MM")
        assert 2 == text.count("3")
        assert 0 == text.count("/")
    except AssertionError:
        printer.print(
            (
                Path(__file__).parent.parent.parent.parent.parent
                / "data"
                / "test_results"
                / "test_gridfinity.pdf"
            ).as_posix()
        )
        raise

    # check if
    assert any(not i.queued_for_printing for i in db_session.query(HardwareItem).all())


def test_gridfinity_no_length(db_session, pdf_text, load_strategy):

    sheet_defs = [LabelSheetDefinition(start_pos=StartPosition(row=20, col=5))]
    printer = Printer.create_printer("GridfinityYml", sheet_defs)

    item = HardwareItem()
    item.main_metric = "MM"
    item.secondary_metric = "BH"
    item.set_for_printing()
    printer.add([item])

    document: BytesIO = printer.print()
    text = pdf_text(document)
    try:
        assert 2 == text.count("MM/BH")
        assert 0 == text.count("None")
    except AssertionError:
        printer.print(
            (
                Path(__file__).parent.parent.parent.parent.parent
                / "data"
                / "test_results"
                / "test_gridfinity.pdf"
            ).as_posix()
        )
        raise

    # check if
    assert any(not i.queued_for_printing for i in db_session.query(HardwareItem).all())
