from fastapi import APIRouter


router = APIRouter(prefix="/api/locations", tags=["Storing Locations"])

@router.get("/", response_model=list[str])
def get_locations():
    return ["Shelf 1", "Shelf 2", "Basement Floor", "Cupboard"]
