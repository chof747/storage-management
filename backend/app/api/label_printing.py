from io import BytesIO
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.schemas import LabelPrintRequest
from app.dependencies import get_db
from app.models import HardwareItem, StorageElement, StorageType
from app.domain.partsbox.partsbox_service import PartsboxService
from app.domain.printing.printer import Printer
from app.schemas.printing_strategy import PrintingSubjectEnum

router = APIRouter(prefix="/api/print", tags=["Hardware Items"])


@router.post("/label")
def print_labels(request: LabelPrintRequest, db: Session = Depends(get_db)):

    printer = Printer.create_printer(request.strategy, request.sheets)

    if not printer.isPrinting(request.subject):
        raise HTTPException(
            status_code=400,
            detail=f'Strategy "{request.strategy}" cannot print subject "{request.subject.value}"',
        )

    hwitems = []
    if request.subject == PrintingSubjectEnum.HARDWARE:
        hwitems = (
            db.query(HardwareItem)
            .join(HardwareItem.storage_element)
            .join(StorageElement.storage_type)
            .filter(HardwareItem.queued_for_printing)
            .all()
        )
        hwitems = [
            item
            for item in hwitems
            if (item.storage_element.storage_type.printing_strategies or {}).get(
                request.subject.value
            )
            == request.strategy
        ]

    parts = []
    if request.subject == PrintingSubjectEnum.ELECTRONIC_PART:
        all_parts = PartsboxService.fetch_parts()
        queued_part_ids = set(PartsboxService.queued_part_ids())
        parts = [p for p in all_parts if p.id in queued_part_ids]

    printer.add(hwitems + parts)

    pdf_stream: BytesIO = printer.print()
    db.commit()
    pdf_stream.seek(0)

    return StreamingResponse(
        pdf_stream,
        media_type="application/pdf",
        headers={"Content-Disposition": "inline; filename=labels.pdf"},
    )
