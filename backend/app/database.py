from supabase import create_client, Client
from app.config import settings
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class Database:
    """Supabase database connection manager"""
    
    def __init__(self):
        self.client: Optional[Client] = None
    
    def connect(self) -> Client:
        """Initialize Supabase client"""
        if not self.client:
            self.client = create_client(
                settings.SUPABASE_URL,
                settings.SUPABASE_KEY
            )
            logger.info("Connected to Supabase")
        return self.client
    
    def get_client(self) -> Client:
        """Get existing client or create new one"""
        if not self.client:
            return self.connect()
        return self.client


# Global database instance
db = Database()


# Helper functions for common operations

async def get_user_by_email(email: str):
    """Get user by email"""
    client = db.get_client()
    result = client.table("users").select("*").eq("email", email).execute()
    return result.data[0] if result.data else None


async def get_user_by_id(user_id: str):
    """Get user by ID"""
    client = db.get_client()
    result = client.table("users").select("*").eq("id", user_id).execute()
    return result.data[0] if result.data else None


async def create_user(email: str, hashed_password: str):
    """Create new user"""
    client = db.get_client()
    result = client.table("users").insert({
        "email": email,
        "password_hash": hashed_password,
        "subscription_tier": "free",
        "credits_remaining": settings.FREE_CREDITS_PER_MONTH
    }).execute()
    return result.data[0] if result.data else None


async def update_user_credits(user_id: str, credits: int):
    """Update user credits"""
    client = db.get_client()
    result = client.table("users").update({
        "credits_remaining": credits
    }).eq("id", user_id).execute()
    return result.data[0] if result.data else None


async def create_video_record(user_id: str, filename: str, file_size_mb: float, 
                             duration_seconds: float, storage_url: str, credits_used: int):
    """Create video record"""
    client = db.get_client()
    result = client.table("videos").insert({
        "user_id": user_id,
        "filename": filename,
        "file_size_mb": file_size_mb,
        "duration_seconds": duration_seconds,
        "storage_url": storage_url,
        "credits_used": credits_used
    }).execute()
    return result.data[0] if result.data else None


async def create_job(user_id: str, video_id: str):
    """Create processing job"""
    client = db.get_client()
    result = client.table("jobs").insert({
        "user_id": user_id,
        "video_id": video_id,
        "status": "pending"
    }).execute()
    return result.data[0] if result.data else None


async def update_job_status(job_id: str, status: str, **kwargs):
    """Update job status and optional fields"""
    client = db.get_client()
    update_data = {"status": status, **kwargs}
    result = client.table("jobs").update(update_data).eq("id", job_id).execute()
    return result.data[0] if result.data else None


async def get_job_by_id(job_id: str):
    """Get job by ID"""
    client = db.get_client()
    result = client.table("jobs").select("*").eq("id", job_id).execute()
    return result.data[0] if result.data else None


async def get_user_jobs(user_id: str, limit: int = 20):
    """Get user's recent jobs"""
    client = db.get_client()
    result = client.table("jobs").select("*").eq("user_id", user_id).order("created_at", desc=True).limit(limit).execute()
    return result.data


async def track_usage(user_id: str, job_id: str, credits_used: int, subscription_tier: str):
    """Track credit usage"""
    client = db.get_client()
    result = client.table("usage").insert({
        "user_id": user_id,
        "job_id": job_id,
        "credits_used": credits_used,
        "subscription_tier": subscription_tier
    }).execute()
    return result.data[0] if result.data else None