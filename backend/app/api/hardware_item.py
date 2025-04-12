from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import SessionLocal
from app.models.hardware_item import HardwareItem
from app.schemas.hardware_item import HardwareItemCreate, HardwareItemUpdate, HardwareItemInDB


router = APIRouter(prefix="/api/items", tags=["Hardware Items"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/", response_model=List[HardwareItemInDB])
def list_items(db: Session = Depends(get_db)):
    return db.query(HardwareItem).all()

@router.post("/", response_model=HardwareItemInDB)
def create_item(item: HardwareItemCreate, db: Session = Depends(get_db)):
    db_item = HardwareItem(**item.dict())
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
