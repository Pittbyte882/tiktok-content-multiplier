from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings from environment variables"""
    
    # App
    APP_NAME: str = "TikTok Content Multiplier"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # API Keys
    ANTHROPIC_API_KEY: str
    OPENAI_API_KEY: str
    
    # Database (Supabase)
    SUPABASE_URL: str
    SUPABASE_KEY: str
    DATABASE_URL: Optional[str] = None
    
    # Storage (S3 or Supabase)
    STORAGE_PROVIDER: str = "supabase"  # "supabase" or "s3"
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_BUCKET_NAME: Optional[str] = None
    AWS_REGION: Optional[str] = "us-east-1"
    
    # Redis (for Celery)
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Stripe
    STRIPE_SECRET_KEY: str
    STRIPE_WEBHOOK_SECRET: str
    STRIPE_PRICE_ID_CREATOR: str  # $49/mo plan
    STRIPE_PRICE_ID_AGENCY: str   # $149/mo plan
    
    # JWT Authentication
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # File Upload Limits
    MAX_VIDEO_SIZE_MB: int = 500  # 500MB max
    MAX_VIDEO_DURATION_MINUTES: int = 5
    ALLOWED_VIDEO_FORMATS: list = ["mp4", "mov", "avi"]
    
    # Credits System
    CREDITS_PER_MINUTE: int = 1  # 1 credit per minute of video
    FREE_CREDITS_PER_MONTH: int = 10  # Free tier
    CREATOR_CREDITS_PER_MONTH: int = 1000  # $49/mo
    AGENCY_CREDITS_PER_MONTH: int = 5000  # $149/mo
    
    # Processing
    MAX_CONCURRENT_JOBS: int = 10
    JOB_TIMEOUT_MINUTES: int = 30
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()