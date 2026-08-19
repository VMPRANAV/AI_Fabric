from fastapi import APIRouter
from app.api.v1.endpoints import health, models, metrics, query

api_router = APIRouter()

api_router.include_router(health.router, tags=["Health"])
api_router.include_router(models.router, tags=["Models"])
api_router.include_router(metrics.router, tags=["Observability"])
api_router.include_router(query.router, tags=["Query Pipeline"])
