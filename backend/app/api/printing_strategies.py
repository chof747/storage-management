from fastapi import APIRouter, HTTPException
from typing import List
from app.domain.printing import get_all_printing_strategies

router = APIRouter(prefix="/api/printing_strategies", tags=["Printing Strategies"])


@router.get("/", response_model=List[str])
def list_items():
    return get_all_printing_strategies()
