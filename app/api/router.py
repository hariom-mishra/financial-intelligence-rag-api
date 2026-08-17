from fastapi import APIRouter
from api.query import router as query_router
from api.upload import router as upload_router

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(query_router)
api_router.include_router(upload_router)

@api_router.get("/health", tags=["Health Check"])
def health_check():
    return {"status": "healthy", "service": "Financial Intelligence API"}
