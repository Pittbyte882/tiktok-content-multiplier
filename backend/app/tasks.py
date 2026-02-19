import asyncio
import logging
import zipfile
from pathlib import Path
from datetime import datetime
from app.agents.transcriber import TranscriberAgent
from app.agents.hook_generator import HookGeneratorAgent
from app.agents.caption_writer import CaptionWriterAgent
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
        caption_writer = CaptionWriterAgent()
        captions = await caption_writer.generate_captions(transcript, hooks)
        
        logger.info(f"Generated {len(captions)} caption variations")
        
        # Step 4: Generate clips
        await update_job_status(job_id, "processing", "Extracting viral clips...")
        clipper = ClipperAgent()
        clips = await clipper.generate_clips(video_path, transcript, segments, target_clips=5)
        
        logger.info(f"Extracted {len(clips)} clips")
        
        # Step 5: Package results
        await update_job_status(job_id, "processing", "Packaging results...")
        
        # Create results dict that package_results will modify
        results_package = {
            'transcript': transcript,
            'hooks': hooks,
            'captions': captions,
            'clips': clips,
            'video_path': video_path
        }
        
        zip_path = await package_results(job_id, results_package)
        
        # Get clip_urls that were added by package_results
        uploaded_clip_urls = results_package.get('clip_urls', [])
        
        logger.info(f"📹 Got {len(uploaded_clip_urls)} clip URLs from package_results")
        
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
            "clip_urls": uploaded_clip_urls,  # ✅ NOW INCLUDED
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
    AND upload clips to Supabase Storage for preview
    """
    from app.database import db
    import shutil
    
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
    
    # Upload clips to Supabase Storage
    clips_dir = output_dir / "clips"
    clips_dir.mkdir(exist_ok=True)
    
    uploaded_clip_urls = []
    
    for i, clip in enumerate(results['clips'], 1):
        clip_source = Path(clip['clip_path'])
        if clip_source.exists():
            # Copy to output directory
            clip_dest = clips_dir / clip_source.name
            shutil.copy2(clip_source, clip_dest)
            
            # Upload to Supabase Storage
            try:
                with open(clip_source, 'rb') as f:
                    clip_data = f.read()
                
                # Upload to Supabase Storage
                storage_path = f"clips/{job_id}/{clip_source.name}"
                
                logger.info(f"Attempting to upload clip {i} to Supabase: {storage_path}")
                
                try:
                    # Try to upload
                    result = db.get_client().storage.from_('videos').upload(
                        storage_path,
                        clip_data,
                        file_options={"content-type": "video/mp4"}
                    )
                    logger.info(f"Upload result: {result}")
                except Exception as upload_error:
                    logger.error(f"Upload failed: {upload_error}")
                    # If file already exists, delete and retry
                    if "already exists" in str(upload_error).lower():
                        logger.info(f"File exists, removing and retrying...")
                        db.get_client().storage.from_('videos').remove([storage_path])
                        result = db.get_client().storage.from_('videos').upload(
                            storage_path,
                            clip_data,
                            file_options={"content-type": "video/mp4"}
                        )
                
                # Get public URL
                public_url = db.get_client().storage.from_('videos').get_public_url(storage_path)
                
                logger.info(f"Uploaded clip {i} to Supabase: {public_url}")
                
                uploaded_clip_urls.append({
                    "clip_number": i,
                    "url": public_url,
                    "start_time": clip['start_time'],
                    "end_time": clip['end_time'],
                    "description": clip['description']
                })
                
            except Exception as e:
                logger.error(f"Failed to upload clip {i} to Supabase: {e}")
    
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
    
    # ✅ STORE CLIP URLS IN RESULTS DICT SO THEY CAN BE ACCESSED
    results['clip_urls'] = uploaded_clip_urls
    
    return str(zip_path)


# For Celery integration (future)
# from celery import Celery
# celery_app = Celery('tasks', broker='redis://localhost:6379/0')
# 
# @celery_app.task
# def process_video_celery(job_id: str, video_path: str):
#     asyncio.run(process_video_job(job_id, video_path))

# Sync wrapper for BackgroundTasks
def process_video_job_sync(job_id: str, video_path: str):
    """Synchronous wrapper for FastAPI BackgroundTasks"""
    import asyncio
    asyncio.run(process_video_job(job_id, video_path))