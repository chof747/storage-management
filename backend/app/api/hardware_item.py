from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.models.hardware_item import HardwareItem
from app.schemas.hardware_item import (
    HardwareItemCreate,
    HardwareItemUpdate,
    HardwareItemInDB,
    HardwareItemPage,
    HardwareItemsMoveRequest,
)
from .pagination import page_parameters


router = APIRouter(prefix="/api/items", tags=["Hardware Items"])


@router.get("/", response_model=HardwareItemPage)
def list_items(pagination=Depends(page_parameters), db: Session = Depends(get_db)):

    total = db.query(HardwareItem).count()
    return {"total": total, "items": pagination(db.query(HardwareItem)).all()}


@router.get("/bystorage", response_model=HardwareItemPage)
def list_items_bystorage(
    storage: int, pagination=Depends(page_parameters), db: Session = Depends(get_db)
):

    q = db.query(HardwareItem).filter(HardwareItem.storage_element_id == storage)
    return {"total": q.count(), "items": pagination(q).all()}


@router.post("/", response_model=HardwareItemInDB)
def create_item(item: HardwareItemCreate, db: Session = Depends(get_db)):
    db_item = HardwareItem(**item.model_dump())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


@router.put("/{item_id}", response_model=HardwareItemInDB)
def update_item(item_id: int, item: HardwareItemUpdate, db: Session = Depends(get_db)):
    db_item = db.get(HardwareItem, item_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    for field, value in item.model_dump(exclude_unset=True).items():
        setattr(db_item, field, value)
    db.commit()
    return db_item


@router.delete("/{item_id}")
def delete_item(item_id: int, db: Session = Depends(get_db)):
    db_item = db.get(HardwareItem, item_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete(db_item)
    db.commit()
    return {"message": "Deleted"}


@router.get("/queueforprinting/{item_id}")
def queue_for_printing(item_id: int, db: Session = Depends(get_db)):
    hw_item: HardwareItem = db.get(HardwareItem, item_id)
    if not hw_item:
        raise HTTPException(status_code=404, detail="Item not found")
    hw_item.set_for_printing()
    db.commit()
    return {"message": f"item {item_id} queued for label printing"}


@router.get("/unqueueforprinting/{item_id}")
def queue_for_printing(item_id: int, db: Session = Depends(get_db)):
    hw_item: HardwareItem = db.get(HardwareItem, item_id)
    if not hw_item:
        raise HTTPException(status_code=404, detail="Item not found")
    hw_item.unset_for_printing()
    db.commit()
    return {"message": f"item {item_id} queued for label printing"}


@router.post("/move")
def move_items(request: HardwareItemsMoveRequest, db: Session = Depends(get_db)):

    for item_id in request.items:
        hw_item: HardwareItem = db.get(HardwareItem, item_id)
        if not hw_item:
            raise HTTPException(status_code=404, detail=f"Item {item_id} not found")
        setattr(hw_item, "storage_element_id", request.storage_to)

    db.commit()
    return {"message": f"Moved {len(request.items)} items to {request.storage_to}"}
