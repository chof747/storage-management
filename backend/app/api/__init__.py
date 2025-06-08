from fastapi import APIRouter
from app.api.hardware_item import router as hardware_item_router
from app.api.storage_type import router as storage_type_router
from app.api.storage_element import router as storage_element_router
from app.api.printing_strategies import router as printing_strategy_router
from app.api.label_printing import router as label_printing_router

api_router = APIRouter()
api_router.include_router(hardware_item_router)
api_router.include_router(storage_element_router)
api_router.include_router(storage_type_router)
api_router.include_router(printing_strategy_router)
api_router.include_router(label_printing_router)
