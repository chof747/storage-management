from fastapi import APIRouter, Query
from typing import List
from app.schemas.partsbox_item import PartsBoxItemPage
from app.domain.partsbox.partsbox_service import PartsboxService

router = APIRouter(prefix="/api/electronic-parts", tags=["Partsbox Items"])


@router.get("/", response_model=PartsBoxItemPage)
def list_partsbox_items(
    limit: int = 10,
    offset: int = 0,
    filters: List[str] = Query(
        None,
        descripiton="Filter in the format key:value. E.g., category:resistor",
    ),
    sort_by: str = "id",
    asc: bool = True,
):

    all_items = PartsboxService.fetch_parts()

    # Filter items if search_key and search_value are provided
    if filters:
        for f in filters:
            key, value = f.split(":", 1)
            all_items = PartsboxService.filter(all_items, key, value)

    total = len(all_items)

    # Sort items
    all_items = PartsboxService.sort(all_items, key=sort_by, ascending=asc)

    # Paginate items
    paginated_items = PartsboxService.paginate(all_items, offset=offset, limit=limit)

    return {"total": total, "items": paginated_items}
