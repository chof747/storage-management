from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, Query as SQLQuery
from typing import List, Optional

from app.dependencies import get_db
from app.models import StorageType
from app.schemas import (
    StorageTypeCreate,
    StorageTypeInDB,
    StorageTypeUpdate,
    StorageTypePage,
)
from app.api.pagination import page_parameters


router = APIRouter(prefix="/api/storagetype", tags=["Storage Types"])


@router.get("/", response_model=StorageTypePage)
@router.get("/{id}", response_model=StorageTypePage)
def list_items(
    id: Optional[int] = None,
    pagination=Depends(page_parameters),
    db: Session = Depends(get_db),
):

    q: SQLQuery = db.query(StorageType)
    q = q.filter(StorageType.id == id) if id is not None else q

    total = q.count()
    return {"total": total, "items": pagination(q).all()}


@router.post("/", response_model=StorageTypeInDB)
def create_item(item: StorageTypeCreate, db: Session = Depends(get_db)):
    db_item = StorageType(**item.model_dump())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


@router.put("/{item_id}", response_model=StorageTypeInDB)
def update_item(item_id: int, item: StorageTypeUpdate, db: Session = Depends(get_db)):
    db_item = db.get(StorageType, item_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    for field, value in item.model_dump(exclude_unset=True).items():
        setattr(db_item, field, value)
    db.commit()
    return db_item


@router.delete("/{item_id}")
def delete_item(item_id: int, db: Session = Depends(get_db)):
    db_item = db.get(StorageType, item_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete(db_item)
    db.commit()
    return {"message": "Deleted"}
