from io import BytesIO
from pathlib import Path
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.schemas import LabelPrintRequest
from app.dependencies import get_db
from app.models import HardwareItem, StorageElement, StorageType
from app.domain.printing.printer import Printer

router = APIRouter(prefix="/api/print", tags=["Hardware Items"])


@router.post("/label")
def print_labels(request: LabelPrintRequest, db: Session = Depends(get_db)):

    items = (
        db.query(HardwareItem)
        .join(HardwareItem.storage_element)
        .join(StorageElement.storage_type)
        .filter(
            HardwareItem.queued_for_printing
            & (StorageType.printing_strategy == request.strategy)
        )
        .all()
    )

    printer = Printer.create_printer(request.strategy, request.sheets)
    printer.add(items)

    pdf_stream: BytesIO = printer.print()
    db.commit()
    pdf_stream.seek(0)

    return StreamingResponse(
        pdf_stream,
        media_type="application/pdf",
        headers={"Content-Disposition": "inline; filename=labels.pdf"},
    )
