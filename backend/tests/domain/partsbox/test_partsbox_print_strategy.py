from pathlib import Path
from pytest import raises, fixture
from app.domain.printing import Printer, LabelSheet, PrintStrategyBase
from io import BytesIO
from app.schemas.printing_strategy import PrintingSubjectEnum
from tests.utils.pdf_test_utils import pdf_text
from app.models import HardwareItem
from app.schemas.label_printing import LabelSheet as LabelSheetDefinition, StartPosition
from app.domain.printing.spec_print_strategy import register_yml_strategy


@fixture
def load_strategy():
    RESOURCE_PATH = Path(__file__).parent.parent.parent / "resources"
    register_yml_strategy(str(RESOURCE_PATH / "partsbox-printing-strategy.yml"))
    return True


def test_partsbox_yml_printer(db_session, pdf_text, load_strategy):

    sheet_defs = [LabelSheetDefinition(start_pos=StartPosition(row=27, col=7))]
    printer = Printer.create_printer("PartsboxGridfinityYml", sheet_defs)

    assert printer.isPrinting(PrintingSubjectEnum.ELECTRONIC_PART)
