from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from app.database import (
    get_user_by_id, 
    create_video_record, 
    create_job, 
    update_user_credits,
    track_usage
)
from app.models import VideoUploadResponse
from app.config import settings
import aiofiles
import os
from datetime import datetime
import uuid

router = APIRouter()


async def get_current_user():
    """
    Get current user from token (placeholder for now)
    In production, decode JWT token from Authorization header
    """
    # TODO: Add real JWT token verification
    # For now, return a mock user for testing
    return {
        "id": "test-user-123",
        "email": "test@example.com",
        "subscription_tier": "free",
        "credits_remaining": 100
    }


def get_video_duration(file_path: str) -> float:
    """Get video duration using ffmpeg"""
    try:
        import ffmpeg
        probe = ffmpeg.probe(file_path)
        duration = float(probe['format']['duration'])
        return duration
    except Exception as e:
        print(f"Error getting duration: {e}")
        return 0.0


@router.post("/upload", response_model=VideoUploadResponse)
async def upload_video(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    """
    Upload video and create processing job
    
    - Validates file type and size
    - Calculates credits needed
    - Saves file to storage
    - Creates job for background processing
    """
    
    # Validate file type
    allowed_types = ["video/mp4", "video/quicktime", "video/x-msvideo"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Only MP4, MOV, and AVI are allowed."
        )
    
    # Read file
    contents = await file.read()
    file_size_mb = len(contents) / (1024 * 1024)
    
    # Validate file size
    if file_size_mb > settings.MAX_VIDEO_SIZE_MB:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size is {settings.MAX_VIDEO_SIZE_MB}MB"
        )
    
    # Save file temporarily
    upload_dir = "/tmp/uploads"
    os.makedirs(upload_dir, exist_ok=True)
    
    file_id = str(uuid.uuid4())
    file_extension = file.filename.split('.')[-1]
    temp_file_path = f"{upload_dir}/{file_id}.{file_extension}"
    
    async with aiofiles.open(temp_file_path, 'wb') as f:
        await f.write(contents)
    
    # Get video duration
    duration_seconds = get_video_duration(temp_file_path)
    duration_minutes = duration_seconds / 60
    
    # Validate duration
    if duration_minutes > settings.MAX_VIDEO_DURATION_MINUTES:
        os.remove(temp_file_path)
        raise HTTPException(
            status_code=400,
            detail=f"Video too long. Maximum duration is {settings.MAX_VIDEO_DURATION_MINUTES} minutes"
        )
    
    # Calculate credits needed (1 credit per minute)
    credits_needed = max(1, int(duration_minutes * settings.CREDITS_PER_MINUTE))
    
    # Check if user has enough credits
    user_credits = current_user.get("credits_remaining", 0)
    if user_credits < credits_needed:
        os.remove(temp_file_path)
        raise HTTPException(
            status_code=402,
            detail=f"Insufficient credits. Need {credits_needed}, have {user_credits}"
        )
    
    # Create video record in database
    video_record = await create_video_record(
        user_id=current_user["id"],
        filename=file.filename,
        file_size_mb=file_size_mb,
        duration_seconds=duration_seconds,
        storage_url=temp_file_path,
        credits_used=credits_needed
    )
    
    # Create processing job
    job_record = await create_job(
        user_id=current_user["id"],
        video_id=video_record["id"]
    )
    
    # Deduct credits
    new_credits = user_credits - credits_needed
    await update_user_credits(current_user["id"], new_credits)
    
    # Track usage
    await track_usage(
        user_id=current_user["id"],
        job_id=job_record["id"],
        credits_used=credits_needed,
        subscription_tier=current_user["subscription_tier"]
    )
    
    # TODO: Trigger Celery task for background processing
    # from app.tasks import process_video
    # process_video.delay(job_record["id"], temp_file_path)
    
    return VideoUploadResponse(
        video_id=video_record["id"],
        job_id=job_record["id"],
        credits_used=credits_needed,
        credits_remaining=new_credits,
        message=f"Upload successful! Processing started. Used {credits_needed} credits."
    )