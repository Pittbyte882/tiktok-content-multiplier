from supabase import create_client, Client
from app.config import settings
import logging
from datetime import datetime
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class Database:
    """Supabase database client"""
    
    def __init__(self):
        self.client: Optional[Client] = None
    
    def connect(self):
        """Initialize Supabase client"""
        try:
            self.client = create_client(
                settings.SUPABASE_URL,
                settings.SUPABASE_KEY
            )
            logger.info("Connected to Supabase")
        except Exception as e:
            logger.error(f"Failed to connect to Supabase: {e}")
            raise
    
    def get_client(self) -> Client:
        """Get Supabase client"""
        if not self.client:
            self.connect()
        return self.client


# Global database instance
db = Database()


# User operations
async def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    """Get user by email"""
    try:
        result = db.get_client().table("users").select("*").eq("email", email).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        logger.error(f"Failed to get user by email: {e}")
        return None


async def get_user_by_id(user_id: str) -> Optional[Dict[str, Any]]:
    """Get user by ID"""
    try:
        result = db.get_client().table("users").select("*").eq("id", user_id).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        logger.error(f"Failed to get user by ID: {e}")
        return None


async def create_user(email: str, password_hash: str) -> Optional[Dict[str, Any]]:
    """Create new user"""
    try:
        user_data = {
            "email": email,
            "password_hash": password_hash,
            "subscription_tier": "free",
            "credits_remaining": 10,  # Free tier starts with 10 credits
            "created_at": datetime.utcnow().isoformat()
        }
        
        result = db.get_client().table("users").insert(user_data).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        logger.error(f"Failed to create user: {e}")
        return None


async def update_user_credits(user_id: str, new_credits: int) -> Optional[Dict[str, Any]]:
    """Update user's credit balance"""
    try:
        result = db.get_client().table("users").update({
            "credits_remaining": new_credits
        }).eq("id", user_id).execute()
        
        return result.data[0] if result.data else None
    except Exception as e:
        logger.error(f"Failed to update credits: {e}")
        return None


# Video operations
async def create_video_record(
    user_id: str,
    filename: str,
    file_size_mb: float,
    duration_seconds: float,
    storage_url: str,
    credits_used: int
) -> Dict[str, Any]:
    """Create video record in database"""
    try:
        video_data = {
            "user_id": user_id,
            "filename": filename,
            "file_size_mb": file_size_mb,
            "duration_seconds": duration_seconds,
            "storage_url": storage_url,
            "credits_used": credits_used,
            "uploaded_at": datetime.utcnow().isoformat()
        }
        
        result = db.get_client().table("videos").insert(video_data).execute()
        return result.data[0]
    except Exception as e:
        logger.error(f"Failed to create video record: {e}")
        raise


# Job operations
async def create_job(user_id: str, video_id: str) -> Dict[str, Any]:
    """Create processing job"""
    try:
        job_data = {
            "user_id": user_id,
            "video_id": video_id,
            "status": "pending",
            "created_at": datetime.utcnow().isoformat()
        }
        
        result = db.get_client().table("jobs").insert(job_data).execute()
        return result.data[0]
    except Exception as e:
        logger.error(f"Failed to create job: {e}")
        raise


async def get_job_by_id(job_id: str) -> Optional[Dict[str, Any]]:
    """Get job by ID"""
    try:
        result = db.get_client().table("jobs").select("*").eq("id", job_id).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        logger.error(f"Failed to get job: {e}")
        return None


async def update_job_status(job_id: str, status: str, message: str = None):
    """Update job status and progress message"""
    try:
        update_data = {
            "status": status,
            "updated_at": datetime.utcnow().isoformat()
        }
        
        if message:
            update_data["error_message"] = message if status == "failed" else None
            
        if status == "processing":
            update_data["started_at"] = datetime.utcnow().isoformat()
        elif status in ["completed", "failed"]:
            update_data["completed_at"] = datetime.utcnow().isoformat()
        
        result = db.get_client().table("jobs").update(update_data).eq("id", job_id).execute()
        
        logger.info(f"Job {job_id} status updated to {status}")
        return result.data[0] if result.data else None
        
    except Exception as e:
        logger.error(f"Failed to update job status: {e}")
        raise


async def update_job_results(job_id: str, results: dict):
    """Update job with final results"""
    try:
        update_data = {
            "status": "completed",
            "transcript": results.get("transcript"),
            "viral_hooks": results.get("viral_hooks"),
            "captions": results.get("captions"),
            "clips": results.get("clips"),
            "clip_urls": results.get("clip_urls"),  # ✅ ADD THIS
            "output_zip_url": results.get("output_zip_url")
        }
        
        # Log what we're saving
        logger.info(f"Saving results for job {job_id}")
        logger.info(f"clip_urls count: {len(results.get('clip_urls', []))}")
        
        result = db.get_client().table("jobs").update(update_data).eq("id", job_id).execute()
        
        logger.info(f"Job {job_id} results updated")
        return result.data[0] if result.data else None
        
    except Exception as e:
        logger.error(f"Failed to update job results: {e}")
        raise


# Usage tracking
async def track_usage(
    user_id: str,
    job_id: str,
    credits_used: int,
    subscription_tier: str
):
    """Track credit usage"""
    try:
        usage_data = {
            "user_id": user_id,
            "job_id": job_id,
            "credits_used": credits_used,
            "subscription_tier": subscription_tier,
            "created_at": datetime.utcnow().isoformat()
        }
        
        result = db.get_client().table("usage").insert(usage_data).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        logger.error(f"Failed to track usage: {e}")
        return None