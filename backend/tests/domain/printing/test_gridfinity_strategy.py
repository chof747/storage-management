from pathlib import Path
from pytest import raises, fixture
from app.domain.printing import Printer, LabelSheet, PrintStrategyBase
from io import BytesIO
from tests.utils.pdf_test_utils import pdf_text
from app.models import HardwareItem


def test_gridfinity_printer(db_session, pdf_text):

    strategy = PrintStrategyBase.create_printing_strategy("Gridfinity")
    sheet = LabelSheet(1, strategy.labelspecs)
    sheet.start_at(20, 5)
    printer = Printer(strategy, [sheet])

    items = db_session.query(HardwareItem)

    added = printer.add([i.as_dict() for i in items])
    assert 2 == added

    document: BytesIO = printer.print()
    text = pdf_text(document)
    try:
        assert "M3" in text
        assert "BH" in text
        assert "5" in text
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
