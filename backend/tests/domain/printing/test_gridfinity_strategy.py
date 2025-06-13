from pathlib import Path
from pytest import raises, fixture
from app.domain.printing import Printer, LabelSheet, PrintStrategyBase
from io import BytesIO
from tests.utils.pdf_test_utils import pdf_text
from app.models import HardwareItem
from app.schemas.label_printing import LabelSheet as LabelSheetDefinition, StartPosition


def test_gridfinity_printer(db_session, pdf_text):

    sheet_defs = [LabelSheetDefinition(start_pos=StartPosition(row=20, col=5))]
    printer = Printer.create_printer("Gridfinity", sheet_defs)

    items = db_session.query(HardwareItem).all()
    for i in items:
        i.queued_for_printing = True
    added = printer.add(items)
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

    # check if
    assert any(not i.queued_for_printing for i in db_session.query(HardwareItem).all())
