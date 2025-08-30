from fastapi import APIRouter
from app.schemas.partsbox_item import PartsBoxItemPage
from app.domain.partsbox.partsbox_service import PartsboxService

router = APIRouter(prefix="/api/electronic-parts", tags=["Partsbox Items"])


@router.get("/", response_model=PartsBoxItemPage)
def list_partsbox_items(
    limit: int = 10,
    offset: int = 0,
    search_key: str = "",
    search_value: str = "",
    sort_by: str = "id",
    asc: bool = True,
):

    all_items = PartsboxService.fetch_parts()

    # Filter items if search_key and search_value are provided
    if search_key and search_value:
        all_items = PartsboxService.filter(all_items, search_key, search_value)

    total = len(all_items)

    # Sort items
    all_items = PartsboxService.sort(all_items, key=sort_by, ascending=asc)

    # Paginate items
    paginated_items = PartsboxService.paginate(all_items, offset=offset, limit=limit)

    return {"total": total, "items": paginated_items}
