from fastapi import APIRouter, HTTPException, Depends, Header
from app.database import get_job_by_id, get_user_by_id
from app.models import JobStatusResponse, JobStatus
from app.config import settings
from jose import jwt, JWTError

router = APIRouter()


async def get_current_user(authorization: str = Header(None)):
    """
    Get current user from JWT token
    Same authentication logic as upload.py
    """
    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Not authenticated"
        )
    
    # Extract token from "Bearer <token>"
    try:
        scheme, token = authorization.split()
        if scheme.lower() != 'bearer':
            raise HTTPException(
                status_code=401,
                detail="Invalid authentication scheme"
            )
    except ValueError:
        raise HTTPException(
            status_code=401,
            detail="Invalid authorization header"
        )
    
    # Decode JWT token
    try:
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        user_id: str = payload.get("user_id")
        if user_id is None:
            raise HTTPException(
                status_code=401,
                detail="Invalid token"
            )
    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Could not validate credentials"
        )
    
    # Get user from database
    user = await get_user_by_id(user_id)
    if user is None:
        raise HTTPException(
            status_code=401,
            detail="User not found"
        )
    
    return user


@router.get("/jobs/{job_id}", response_model=JobStatusResponse)
async def get_job_status(
    job_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get job processing status and results
    
    - Returns current status (pending, processing, completed, failed)
    - Includes progress percentage
    - Returns results when completed
    - Requires authentication
    """
    
    # Get job from database
    job = await get_job_by_id(job_id)
    
    if not job:
        raise HTTPException(
            status_code=404,
            detail="Job not found"
        )
    
    # Verify user owns this job
    if job["user_id"] != current_user["id"]:
        raise HTTPException(
            status_code=403,
            detail="Access denied"
        )
    
    # Calculate progress percentage
    progress_map = {
        "pending": 0,
        "processing": 50,
        "completed": 100,
        "failed": 0
    }
    progress = progress_map.get(job["status"], 0)
    
    # Build response
    response = JobStatusResponse(
        job_id=job["id"],
        status=job["status"],
        progress_percent=progress,
        message=job.get("error_message") or f"Job is {job['status']}"
    )
    
    # Add results if completed
    if job["status"] == "completed":
        response.results = {
            "transcript": job.get("transcript", ""),
            "viral_hooks": job.get("viral_hooks", []),
            "captions": job.get("captions", []),
            "clips": job.get("clips", []),
            "download_url": job.get("output_zip_url")
        }
    
    return response