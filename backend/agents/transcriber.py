from openai import OpenAI
from app.config import settings
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class TranscriberAgent:
    """
    AI agent that transcribes video audio using OpenAI Whisper
    
    Extracts audio from video and generates accurate transcript
    with timestamps for viral moment detection.
    """
    
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
    
    async def transcribe_video(self, video_path: str) -> dict:
        """
        Transcribe video audio
        
        Args:
            video_path: Path to video file
            
        Returns:
            dict with:
                - text: Full transcript
                - duration: Video duration in seconds
                - language: Detected language
        """
        try:
            # Extract audio from video first (we'll need ffmpeg)
            audio_path = await self._extract_audio(video_path)
            
            # Transcribe with Whisper
            logger.info(f"Transcribing video: {video_path}")
            
            with open(audio_path, "rb") as audio_file:
                transcript = self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    response_format="verbose_json",  # Get timestamps
                    language="en"  # Can detect automatically by omitting this
                )
            
            result = {
                "text": transcript.text,
                "duration": transcript.duration if hasattr(transcript, 'duration') else 0,
                "language": transcript.language if hasattr(transcript, 'language') else "en",
                "segments": transcript.segments if hasattr(transcript, 'segments') else []
            }
            
            logger.info(f"Transcription complete: {len(result['text'])} chars")
            
            # Cleanup temp audio file
            Path(audio_path).unlink(missing_ok=True)
            
            return result
            
        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            raise
    
    async def _extract_audio(self, video_path: str) -> str:
        """
        Extract audio from video using ffmpeg
        
        Args:
            video_path: Path to video file
            
        Returns:
            Path to extracted audio file (mp3)
        """
        import ffmpeg
        
        output_path = video_path.replace('.mp4', '_audio.mp3').replace('.mov', '_audio.mp3')
        
        try:
            # Extract audio with ffmpeg
            stream = ffmpeg.input(video_path)
            stream = ffmpeg.output(stream, output_path, acodec='libmp3lame', ab='192k')
            ffmpeg.run(stream, capture_stdout=True, capture_stderr=True, overwrite_output=True)
            
            logger.info(f"Audio extracted: {output_path}")
            return output_path
            
        except ffmpeg.Error as e:
            logger.error(f"FFmpeg audio extraction failed: {e.stderr.decode()}")
            raise
    
    def get_video_duration(self, video_path: str) -> float:
        """Get video duration in seconds using ffmpeg"""
        import ffmpeg
        
        try:
            probe = ffmpeg.probe(video_path)
            duration = float(probe['format']['duration'])
            return duration
        except Exception as e:
            logger.error(f"Failed to get video duration: {e}")
            return 0.0


# Example usage
if __name__ == "__main__":
    import asyncio
    
    async def test():
        agent = TranscriberAgent()
        
        # Test with a sample video
        video_path = "/path/to/test/video.mp4"
        
        result = await agent.transcribe_video(video_path)
        
        print(f"Transcript ({len(result['text'])} chars):")
        print(result['text'][:500] + "...")
        print(f"\nDuration: {result['duration']} seconds")
        print(f"Language: {result['language']}")
    
    # asyncio.run(test())
    print("Transcriber agent ready")