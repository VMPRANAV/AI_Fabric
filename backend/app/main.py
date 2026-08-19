from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.config import settings
from core.logging import logger
from core.database import init_db
from api.v1.router import api_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing AI Fabric backend...")
    try:
        await init_db()
        logger.info("AI Fabric database initialization completed.")
    except Exception as e:
        logger.warning(f"Database init warning: {e}. Ensure DATABASE_URL is accessible.")
    yield
    logger.info("Shutting down AI Fabric backend...")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="AI Fabric: Intelligent Control Plane & Adaptive Routing Platform for AI Resources",
    lifespan=lifespan
)

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust as needed in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API v1 routes
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/", summary="Root Status")
async def root():
    return {
        "message": "AI Fabric Control Plane is active.",
        "docs": "/docs",
        "api_v1": settings.API_V1_STR,
        "health": f"{settings.API_V1_STR}/health"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=settings.PORT, reload=settings.DEBUG)
