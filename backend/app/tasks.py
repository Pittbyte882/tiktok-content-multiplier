import asyncio
import logging
import zipfile
from pathlib import Path
from datetime import datetime
from app.agents.transcriber import TranscriberAgent
from app.agents.hook_generator import HookGeneratorAgent
from app.agents.caption_generator import CaptionGeneratorAgent
from app.agents.clipper import ClipperAgent
from app.database import update_job_status, update_job_results

logger = logging.getLogger(__name__)


async def process_video_job(job_id: str, video_path: str):
    """
    Main video processing pipeline
    
    Steps:
    1. Transcribe audio
    2. Generate viral hooks
    3. Generate captions + hashtags
    4. Identify and extract clips
    5. Package everything into ZIP
    6. Update job with results
    
    Args:
        job_id: Job ID from database
        video_path: Path to uploaded video file
    """
    
    logger.info(f"Starting processing for job {job_id}")
    
    try:
        # Update status to processing
        await update_job_status(job_id, "processing", "Transcribing audio...")
        
        # Step 1: Transcribe
        transcriber = TranscriberAgent()
        transcript_result = await transcriber.transcribe_video(video_path)
        transcript = transcript_result['text']
        segments = transcript_result.get('segments', [])
        
        logger.info(f"Transcription complete: {len(transcript)} characters")
        
        # Step 2: Generate viral hooks
        await update_job_status(job_id, "processing", "Generating viral hooks...")
        hook_generator = HookGeneratorAgent()
        hooks = await hook_generator.generate_hooks(transcript)
        
        logger.info(f"Generated {len(hooks)} viral hooks")
        
        # Step 3: Generate captions
        await update_job_status(job_id, "processing", "Creating captions...")
        caption_generator = CaptionGeneratorAgent()
        captions = await caption_generator.generate_captions(transcript, hooks)
        
        logger.info(f"Generated {len(captions)} caption variations")
        
        # Step 4: Generate clips
        await update_job_status(job_id, "processing", "Extracting viral clips...")
        clipper = ClipperAgent()
        clips = await clipper.generate_clips(video_path, transcript, segments, target_clips=20)
        
        logger.info(f"Extracted {len(clips)} clips")
        
        # Step 5: Package results
        await update_job_status(job_id, "processing", "Packaging results...")
        zip_path = await package_results(job_id, {
            'transcript': transcript,
            'hooks': hooks,
            'captions': captions,
            'clips': clips,
            'video_path': video_path
        })
        
        # Step 6: Update job with results
        await update_job_results(job_id, {
            "status": "completed",
            "transcript": transcript,
            "viral_hooks": hooks,
            "captions": captions,
            "clips": [
                {
                    "start_time": clip['start_time'],
                    "end_time": clip['end_time'],
                    "duration": clip['duration'],
                    "description": clip['description']
                }
                for clip in clips
            ],
            "output_zip_url": zip_path,
            "completed_at": datetime.utcnow().isoformat()
        })
        
        logger.info(f"Job {job_id} completed successfully")
        
    except Exception as e:
        logger.error(f"Job {job_id} failed: {e}", exc_info=True)
        await update_job_status(
            job_id, 
            "failed", 
            f"Processing failed: {str(e)}"
        )


async def package_results(job_id: str, results: dict) -> str:
    """
    Package all results into a downloadable ZIP file
    
    Contents:
    - transcript.txt
    - viral_hooks.txt
    - captions/caption_01.txt ... caption_10.txt
    - clips/clip_01.mp4 ... clip_20.mp4
    
    Returns:
        Path to ZIP file
    """
    
    output_dir = Path("/tmp/outputs") / job_id
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Create transcript file
    transcript_path = output_dir / "transcript.txt"
    transcript_path.write_text(results['transcript'])
    
    # Create hooks file
    hooks_path = output_dir / "viral_hooks.txt"
    hooks_text = "\n\n".join([f"{i}. {hook}" for i, hook in enumerate(results['hooks'], 1)])
    hooks_path.write_text(hooks_text)
    
    # Create captions directory
    captions_dir = output_dir / "captions"
    captions_dir.mkdir(exist_ok=True)
    
    for i, caption_data in enumerate(results['captions'], 1):
        caption_file = captions_dir / f"caption_{i:02d}.txt"
        caption_text = f"{caption_data['caption']}\n\n{' '.join(caption_data['hashtags'])}"
        caption_file.write_text(caption_text)
    
    # Copy clips to directory
    clips_dir = output_dir / "clips"
    clips_dir.mkdir(exist_ok=True)
    
    for clip in results['clips']:
        clip_source = Path(clip['clip_path'])
        if clip_source.exists():
            clip_dest = clips_dir / clip_source.name
            import shutil
            shutil.copy2(clip_source, clip_dest)
    
    # Create README
    readme_path = output_dir / "README.txt"
    readme_text = f"""🎬 StackSlice AI - Video Processing Results
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

📁 Contents:
- transcript.txt: Full video transcription
- viral_hooks.txt: {len(results['hooks'])} viral hook variations
- captions/: {len(results['captions'])} caption + hashtag combinations
- clips/: {len(results['clips'])} viral-ready video clips

🚀 How to use:
1. Pick your favorite hooks from viral_hooks.txt
2. Choose a caption from captions/ that matches your vibe
3. Upload clips from clips/ to TikTok
4. Watch your engagement soar!

Need help? Contact support@stacksliceai.com
"""
    readme_path.write_text(readme_text)
    
    # Create ZIP file
    zip_path = output_dir.parent / f"{job_id}_results.zip"
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file in output_dir.rglob('*'):
            if file.is_file():
                arcname = file.relative_to(output_dir)
                zipf.write(file, arcname)
    
    logger.info(f"Results packaged: {zip_path}")
    
    # TODO: Upload ZIP to cloud storage (S3, Supabase Storage, etc.)
    # For now, return local path
    
    return str(zip_path)


# For Celery integration (future)
# from celery import Celery
# celery_app = Celery('tasks', broker='redis://localhost:6379/0')
# 
# @celery_app.task
# def process_video_celery(job_id: str, video_path: str):
#     asyncio.run(process_video_job(job_id, video_path))