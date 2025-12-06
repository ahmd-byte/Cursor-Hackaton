"""
API module - Contains all API version routers.
"""

from fastapi import APIRouter

from app.api.v1 import router as v1_router

# Main API router
api_router = APIRouter()

# Include version routers
api_router.include_router(v1_router, prefix="/v1")

