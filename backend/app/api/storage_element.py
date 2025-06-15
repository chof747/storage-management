from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, Query as SQLQuery
from typing import List, Optional

from app.dependencies import get_db
from app.models import StorageElement, HardwareItem
from app.schemas import (
    StorageElementCreate,
    StorageElementInDB,
    StorageElementUpdate,
    StorageElementPage,
)
from app.api.pagination import page_parameters

router = APIRouter(prefix="/api/storage", tags=["Storage Elements"])


@router.get("/", response_model=StorageElementPage)
@router.get("/{id}", response_model=StorageElementPage)
def list_items(
    id: Optional[int] = None,
    pagination=Depends(page_parameters),
    db: Session = Depends(get_db),
):

    q: SQLQuery = db.query(StorageElement)
    q = q.filter(StorageElement.id == id) if id is not None else q

    total = q.count()
    return {"total": total, "items": pagination(q).all()}


@router.post("/", response_model=StorageElementInDB)
def create_item(item: StorageElementCreate, db: Session = Depends(get_db)):
    db_item = StorageElement(**item.model_dump())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


@router.put("/{item_id}", response_model=StorageElementInDB)
def update_item(
    item_id: int, item: StorageElementUpdate, db: Session = Depends(get_db)
):
    db_item = db.get(StorageElement, item_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    for field, value in item.model_dump(exclude_unset=True).items():
        setattr(db_item, field, value)
    db.commit()
    return db_item


@router.delete("/{item_id}")
def delete_item(item_id: int, db: Session = Depends(get_db)):
    db_item = db.get(StorageElement, item_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete(db_item)
    db.commit()
    return {"message": "Deleted"}


@router.post("/markallforprinting/{item_id}")
def mark_all_for_printing(item_id: int, db: Session = Depends(get_db)):
    items = (
        db.query(HardwareItem)
        .join(HardwareItem.storage_element)
        .filter(StorageElement.id == item_id)
        .all()
    )

    for item in items:
        item.queued_for_printing = True
    db.commit()

    return {"message": f"{len(items)} marked for printing"}
