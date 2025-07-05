from io import BytesIO
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from app.domain.printing.spec_print_strategy import register_yml_strategy

from app.models.hardware_item import HardwareItem
from app.models.storage_type import StorageType
from tests.utils.pdf_test_utils import pdf_text


@pytest.fixture
def load_strategy():
    RESOURCE_PATH = Path(__file__).parent.parent / "resources"
    register_yml_strategy(str(RESOURCE_PATH / "print-strategy-test.yml"))
    return True


def test_print_labels_pdf_generation(client, pdf_text, db_session, load_strategy):
    request_data = {
        "sheets": [
            {"start_pos": {"row": 1, "col": 1}},
            {"start_pos": {"row": 2, "col": 3}},
        ],
        "strategy": "GridfinityYml",
    }

    st = db_session.get(StorageType, 1)
    st.printing_strategy = "GridfinityYml"
    db_session.commit()

    response = client.post("/api/print/label", json=request_data)
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert "filename=labels.pdf" in response.headers.get("content-disposition", "")

    pdf_bytes = response.content
    text = pdf_text(BytesIO(pdf_bytes))
    try:
        assert "M3" in text
        assert "BH" in text
        assert "5" in text
    except AssertionError:
        with open(
            (
                Path(__file__).parent.parent.parent.parent.parent
                / "data"
                / "test_results"
                / "test_gridfinity.pdf"
            ).as_posix(),
            "wb",
        ) as f:
            f.write(pdf_bytes)

        raise
    assert pdf_bytes.startswith(b"%PDF"), "Not a valid PDF file"
