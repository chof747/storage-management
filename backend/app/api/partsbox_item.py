from fastapi import APIRouter, Query
from typing import List
from app.schemas.partsbox_item import PartsBoxItemPage
from app.domain.partsbox.partsbox_service import PartsboxService

router = APIRouter(prefix="/api/electronic-parts", tags=["Partsbox Items"])


@router.get("/", response_model=PartsBoxItemPage)
def list_partsbox_items(
    limit: int = 10,
    offset: int = 0,
    filter: List[str] = Query(
        None,
        descripiton="Filter in the format key:value. E.g., category:resistor",
    ),
    sort_by: str = "name",
    asc: bool = True,
):

    all_items = PartsboxService.fetch_parts()

    # Filter items if search_key and search_value are provided
    if filter:
        for f in filter:
            key, value = f.split(":", 1)
            all_items = PartsboxService.filter(all_items, key, value)

    total = len(all_items)

    printing_queue = PartsboxService.queued_part_ids()

    for item in all_items:
        item.queued_for_printing = item.id in printing_queue

    # Sort items
    all_items = PartsboxService.sort(all_items, key=sort_by, ascending=asc)

    # Paginate items
    paginated_items = PartsboxService.paginate(all_items, offset=offset, limit=limit)

    return {"total": total, "items": paginated_items}


@router.get("/queueforprinting/{item_id}")
def queue_for_printing(item_id: str):
    PartsboxService.queue_for_printing(item_id)
    return {"message": f"electronic-part {item_id} queued for label printing"}


@router.get("/unqueueforprinting/{item_id}")
def unqueue_for_printing(item_id: str):
    PartsboxService.unqueue_for_printing(item_id)
    return {"message": f"electronic-part {item_id} unqueued for label printing"}
