from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.hardware_item import HardwareItem
from app.schemas.hardware_item import HardwareItemCreate, HardwareItemUpdate, HardwareItemInDB, HardwareItemPage
from .pagination import page_parameters


router = APIRouter(prefix="/api/items", tags=["Hardware Items"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/", response_model=HardwareItemPage)
def list_items(
    pagination = Depends(page_parameters),
    db: Session = Depends(get_db)):

    total = db.query(HardwareItem).count()
    return {
        "total": total,
        "items" : pagination(db.query(HardwareItem)).all()
    }

@router.get("/bystorage", response_model=HardwareItemPage)
def list_items_bystorage(
    storage: int,
    pagination = Depends(page_parameters),
    db: Session = Depends(get_db)):    

    q = db.query(HardwareItem).filter(HardwareItem.storage_element_id == storage)
    return {
        "total": q.count(),
        "items": pagination(q).all()
    }

        

@router.post("/", response_model=HardwareItemInDB)
def create_item(item: HardwareItemCreate, db: Session = Depends(get_db)):
    db_item = HardwareItem(**item.model_dump())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@router.put("/{item_id}", response_model=HardwareItemInDB)
def update_item(item_id: int, item: HardwareItemUpdate, db: Session = Depends(get_db)):
    db_item = db.query(HardwareItem).get(item_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    for field, value in item.dict(exclude_unset=True).items():
        setattr(db_item, field, value)
    db.commit()
    return db_item

@router.delete("/{item_id}")
def delete_item(item_id: int, db: Session = Depends(get_db)):
    db_item = db.query(HardwareItem).get(item_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete(db_item)
    db.commit()
    return {"message": "Deleted"}

@router.get("/queueforprinting/{item_id}")
def queue_for_printing(item_id: int, db: Session = Depends(get_db)):
    hw_item : HardwareItem = db.query(HardwareItem).get(item_id)
    if not hw_item:
        raise HTTPException(status_code=404, detail="Item not found")
    setattr(hw_item, "queued_for_printing", 1)
    db.commit()
    return {"message": f"item {item_id} queued for label printing"}

@router.get("/unqueueforprinting/{item_id}")
def queue_for_printing(item_id: int, db: Session = Depends(get_db)):
    hw_item : HardwareItem = db.query(HardwareItem).get(item_id)
    if not hw_item:
        raise HTTPException(status_code=404, detail="Item not found")
    setattr(hw_item, "queued_for_printing", 0)
    db.commit()
    return {"message": f"item {item_id} queued for label printing"}
