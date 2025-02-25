from fastapi import APIRouter
from .endpoints import data, collection

api_router = APIRouter()
api_router.include_router(data.router, prefix="/data", tags=["data"])
api_router.include_router(collection.router, prefix="/collection", tags=["collection"])
