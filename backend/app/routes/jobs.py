from fastapi import APIRouter, HTTPException, Depends
from app.database import get_job_by_id
from app.models import JobStatusResponse, JobStatus

router = APIRouter()


async def get_current_user():
    """Get current user (placeholder)"""
    return {
        "id": "test-user-123",
        "email": "test@example.com"
    }


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