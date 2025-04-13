from fastapi import APIRouter
from app.api.hardware_item import router as hardware_item_router
from  app.api.locations import router as location_router

api_router = APIRouter()
api_router.include_router(hardware_item_router)
api_router.include_router(location_router)  # 👈 add this
