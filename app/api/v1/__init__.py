"""
API v1 module - Contains all v1 endpoints.
"""

from fastapi import APIRouter

from app.api.v1 import auth, buckets, wages, ai_agent, documents

# v1 router
router = APIRouter()

# Include all endpoint routers
router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
router.include_router(buckets.router, prefix="/buckets", tags=["Money Jars (Buckets)"])
router.include_router(wages.router, prefix="/wages", tags=["Early Wage Access"])
router.include_router(ai_agent.router, prefix="/ai", tags=["AI Agent"])
router.include_router(documents.router, prefix="/documents", tags=["Document Processing"])

