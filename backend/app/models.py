from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr
from enum import Enum


class SubscriptionTier(str, Enum):
    """Subscription tiers"""
    FREE = "free"
    CREATOR = "creator"
    AGENCY = "agency"


class JobStatus(str, Enum):
    """Job processing statuses"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


# Database Models (for Supabase tables)

class User(BaseModel):
    """User account"""
    id: str
    email: EmailStr
    created_at: datetime
    subscription_tier: SubscriptionTier = SubscriptionTier.FREE
    stripe_customer_id: Optional[str] = None
    credits_remaining: int = 10  # Free tier starts with 10
    credits_reset_date: Optional[datetime] = None


class Video(BaseModel):
    """Uploaded video"""
    id: str
    user_id: str
    filename: str
    file_size_mb: float
    duration_seconds: float
    storage_url: str
    uploaded_at: datetime
    credits_used: int


class Job(BaseModel):
    """Processing job"""
    id: str
    user_id: str
    video_id: str
    status: JobStatus = JobStatus.PENDING
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    
    # Results
    transcript: Optional[str] = None
    viral_hooks: Optional[List[str]] = None
    captions: Optional[List[dict]] = None
    clips: Optional[List[dict]] = None
    output_zip_url: Optional[str] = None


class Usage(BaseModel):
    """Track credit usage"""
    id: str
    user_id: str
    job_id: str
    credits_used: int
    created_at: datetime
    subscription_tier: SubscriptionTier


# API Schemas (Request/Response models)

class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class VideoUploadResponse(BaseModel):
    video_id: str
    job_id: str
    credits_used: int
    credits_remaining: int
    message: str


class JobStatusResponse(BaseModel):
    job_id: str
    status: JobStatus
    progress_percent: int
    message: str
    results: Optional[dict] = None


class GenerationResult(BaseModel):
    """Final generation results"""
    job_id: str
    video_id: str
    
    # Transcription
    transcript: str
    
    # Generated content
    viral_hooks: List[str]  # 5-10 hook variations
    captions: List[dict]    # Caption + hashtag combos
    clips: List[dict]       # Clip metadata (start, end, description)
    clip_urls: Optional[List[Dict]] = None
    
    # Download
    download_url: str
    
    # Metadata
    credits_used: int
    processing_time_seconds: float
    created_at: datetime


class SubscriptionUpdate(BaseModel):
    """Stripe subscription webhook"""
    user_id: str
    tier: SubscriptionTier
    stripe_subscription_id: str