# backend/app/api/api.py
from fastapi import APIRouter
from .endpoints import data, query

api_router = APIRouter()
api_router.include_router(data.router, prefix="/data", tags=["data"])
api_router.include_router(query.router, prefix="/query", tags=["query"])
