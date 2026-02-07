from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import db
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-powered TikTok content multiplier - turn 1 video into 20+ pieces of content",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Initialize connections on startup"""
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    db.connect()
    logger.info("Database connected")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down application")


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "healthy",
        "message": "TikTok Content Multiplier API is running"
    }


@app.get("/health")
async def health_check():
    """Detailed health check"""
    try:
        # Check database connection
        client = db.get_client()
        # Simple query to verify connection
        client.table("users").select("count", count="exact").limit(0).execute()
        
        return {
            "status": "healthy",
            "database": "connected",
            "version": settings.APP_VERSION
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unhealthy")


# Import routers (we'll create these next)
# from app.routes import upload, jobs, auth, payments
# app.include_router(auth.router, prefix="/auth", tags=["authentication"])
# app.include_router(upload.router, prefix="/upload", tags=["upload"])
# app.include_router(jobs.router, prefix="/jobs", tags=["jobs"])
# app.include_router(payments.router, prefix="/payments", tags=["payments"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )