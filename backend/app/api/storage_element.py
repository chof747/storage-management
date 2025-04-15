from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import SessionLocal
from app.models import StorageElement
from app.schemas import StorageElementCreate, StorageElementInDB, StorageElementUpdate


router = APIRouter(prefix="/api/storage", tags=["Storage Elements"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/", response_model=List[StorageElementInDB])
def list_items(db: Session = Depends(get_db)):
    return db.query(StorageElement).all()

@router.post("/", response_model=StorageElementInDB)
def create_item(item: StorageElementCreate, db: Session = Depends(get_db)):
    db_item = StorageElement(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@router.put("/{item_id}", response_model=StorageElementInDB)
def update_item(item_id: int, item: StorageElementUpdate, db: Session = Depends(get_db)):
    db_item = db.query(StorageElement).get(item_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    for field, value in item.dict(exclude_unset=True).items():
        setattr(db_item, field, value)
    db.commit()
    return db_item

@router.delete("/{item_id}")
def delete_item(item_id: int, db: Session = Depends(get_db)):
    db_item = db.query(StorageElement).get(item_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete(db_item)
    db.commit()
    return {"message": "Deleted"}
