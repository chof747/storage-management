from pytest import fixture
from PyPDF2 import PdfReader


@fixture
def pdf_text():
    def _extract(buffer):
        reader = PdfReader(buffer)
        return "".join([p.extract_text() for p in reader.pages])

    return _extract
