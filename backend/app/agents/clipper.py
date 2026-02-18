from anthropic import Anthropic
from app.config import settings
import ffmpeg
import logging
from typing import List, Dict
from pathlib import Path

logger = logging.getLogger(__name__)


class ClipperAgent:
    """
    AI agent that identifies and extracts viral-worthy clips
    
    Analyzes transcript to find the best moments, then cuts
    the video into 20+ short-form clips optimized for TikTok.
    """
    
    def __init__(self):
        self.client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.model = "claude-sonnet-4-20250514"
    
    async def generate_clips(
        self,
        video_path: str,
        transcript: str,
        transcript_segments: List[Dict] = None,
        target_clips: int = 20
    ) -> List[Dict]:
        """
        Identify viral moments and create clips
        
        Args:
            video_path: Path to original video
            transcript: Full transcript text
            transcript_segments: Whisper segments with timestamps
            target_clips: Number of clips to generate (default 20)
            
        Returns:
            List of clip metadata dicts with:
                - clip_path: Path to extracted clip
                - start_time: Start timestamp (seconds)
                - end_time: End timestamp (seconds)
                - duration: Clip duration
                - description: What makes this clip viral
                - score: Viral potential score (0-100)
        """
        try:
            # Step 1: AI identifies viral moments
            viral_moments = await self._identify_viral_moments(
                transcript, 
                transcript_segments,
                target_clips
            )
            
            logger.info(f"AI identified {len(viral_moments)} viral moments")
            
            # Step 2: Extract clips from video
            clips = await self._extract_clips(video_path, viral_moments)
            
            logger.info(f"Generated {len(clips)} clips from video")
            return clips
            
        except Exception as e:
            logger.error(f"Clip generation failed: {e}")
            return []
    
    async def _identify_viral_moments(
        self,
        transcript: str,
        segments: List[Dict],
        target_count: int
    ) -> List[Dict]:
        """Use AI to identify the best moments for clips"""
        
        prompt = f"""You are a TikTok video editor expert at finding viral moments.

Video transcript:
{transcript}

Your task: Identify the {target_count} BEST moments from this video that would make viral TikTok clips.

VIRAL MOMENT CRITERIA:
1. Hook potential - grabs attention immediately
2. Value density - packs insight/entertainment quickly
3. Emotional impact - makes people feel something
4. Shareability - people want to send this
5. Standalone quality - works without full context
6. Optimal length - 15-60 seconds ideal

For each moment, provide:
- Approximate start/end timestamps
- Why it's viral-worthy
- Key soundbite or visual
- Viral potential score (0-100)

Format EXACTLY like this:
1.
START: 00:15
END: 00:42
DESCRIPTION: Shows the shocking before/after transformation
SCORE: 95

2.
START: 01:23
END: 01:58
DESCRIPTION: The aha moment where technique is revealed
SCORE: 88

Continue for {target_count} moments. Prioritize VARIETY - different types of hooks, emotions, content angles."""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4000,
                temperature=0.7,
                messages=[{"role": "user", "content": prompt}]
            )
            
            response_text = response.content[0].text
            logger.info(f"Received AI response: {len(response_text)} characters")
            
            moments = self._parse_viral_moments(response_text)
            
            # If we have segments with precise timestamps, refine the times
            if segments:
                moments = self._refine_timestamps(moments, segments, transcript)
            
            return moments
            
        except Exception as e:
            logger.error(f"AI moment identification failed: {e}")
            return self._fallback_moments(transcript, target_count)
    
    def _parse_viral_moments(self, response_text: str) -> List[Dict]:
        """Parse viral moments from AI response"""
        moments = []
        
        # Log the raw response
        logger.info(f"🔍 Raw AI response length: {len(response_text)} chars")
        logger.info(f"🔍 First 500 chars: {response_text[:500]}")
        
        # Try to parse numbered sections (1., 2., 3., etc.)
        lines = response_text.split('\n')
        current_moment = {}
        
        for line in lines:
            line = line.strip()
            
            if not line:
                continue
                
            # Check for START timestamp
            if 'START:' in line.upper():
                try:
                    time_str = line.split(':', 1)[1].strip()
                    current_moment['start_time'] = self._parse_timestamp(time_str)
                    logger.info(f"Found START: {current_moment['start_time']}")
                except Exception as e:
                    logger.error(f"Failed to parse START: {line} - {e}")
                    
            # Check for END timestamp
            elif 'END:' in line.upper():
                try:
                    time_str = line.split(':', 1)[1].strip()
                    current_moment['end_time'] = self._parse_timestamp(time_str)
                    logger.info(f"Found END: {current_moment['end_time']}")
                except Exception as e:
                    logger.error(f"Failed to parse END: {line} - {e}")
                    
            # Check for DESCRIPTION
            elif 'DESCRIPTION:' in line.upper():
                try:
                    desc = line.split(':', 1)[1].strip()
                    current_moment['description'] = desc
                    logger.info(f"Found DESCRIPTION: {desc[:50]}...")
                except Exception as e:
                    logger.error(f"Failed to parse DESCRIPTION: {line} - {e}")
                    
            # Check for SCORE
            elif 'SCORE:' in line.upper():
                try:
                    score_str = line.split(':', 1)[1].strip()
                    current_moment['score'] = int(score_str)
                    logger.info(f"Found SCORE: {current_moment['score']}")
                    
                    # If we have all fields, save the moment
                    if all(k in current_moment for k in ['start_time', 'end_time', 'description', 'score']):
                        current_moment['duration'] = current_moment['end_time'] - current_moment['start_time']
                        moments.append(current_moment.copy())
                        logger.info(f"✅ Added moment: {current_moment['start_time']}s - {current_moment['end_time']}s")
                        current_moment = {}
                except Exception as e:
                    logger.error(f"Failed to parse SCORE: {line} - {e}")
        
        logger.info(f"📊 Total moments found: {len(moments)}")
        
        # Sort by score
        moments.sort(key=lambda x: x['score'], reverse=True)
        return moments[:20]  # Max 20 clips
    
    def _parse_timestamp(self, timestamp_str: str) -> float:
        """Convert MM:SS or HH:MM:SS to seconds"""
        parts = timestamp_str.strip().split(':')
        if len(parts) == 2:  # MM:SS
            return int(parts[0]) * 60 + int(parts[1])
        elif len(parts) == 3:  # HH:MM:SS
            return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
        return 0
    
    def _refine_timestamps(
        self,
        moments: List[Dict],
        segments: List[Dict],
        transcript: str
    ) -> List[Dict]:
        """Refine timestamps using Whisper's precise segment data"""
        # TODO: Match moment descriptions to actual transcript segments
        # For now, return as-is
        return moments
    
    async def _extract_clips(self, video_path: str, moments: List[Dict]) -> List[Dict]:
        """Extract actual video clips using ffmpeg"""
        clips = []
        video_dir = Path(video_path).parent
        video_name = Path(video_path).stem
        
        logger.info(f"📹 Extracting {len(moments)} clips from {video_path}")
        
        for i, moment in enumerate(moments, 1):
            try:
                output_path = video_dir / f"{video_name}_clip_{i:02d}.mp4"
                
                logger.info(f"Extracting clip {i}: {moment['start_time']}s - {moment['end_time']}s ({moment['duration']}s)")
                
                # Extract clip with ffmpeg
                (
                    ffmpeg
                    .input(video_path, ss=moment['start_time'], t=moment['duration'])
                    .output(
                        str(output_path),
                        vcodec='libx264',
                        acodec='aac',
                        **{'b:v': '2M', 'b:a': '128k'}
                    )
                    .overwrite_output()
                    .run(capture_stdout=True, capture_stderr=True, quiet=True)
                )
                
                clips.append({
                    "clip_path": str(output_path),
                    "start_time": moment['start_time'],
                    "end_time": moment['end_time'],
                    "duration": moment['duration'],
                    "description": moment['description'],
                    "score": moment['score']
                })
                
                logger.info(f"✅ Extracted clip {i}: {moment['duration']:.1f}s at {moment['start_time']:.1f}s")
                
            except ffmpeg.Error as e:
                logger.error(f"❌ FFmpeg clip extraction failed for clip {i}: {e.stderr.decode() if e.stderr else str(e)}")
                continue
            except Exception as e:
                logger.error(f"❌ Failed to extract clip {i}: {e}")
                continue
        
        logger.info(f"📊 Successfully extracted {len(clips)} clips")
        return clips
    
    def _fallback_moments(self, transcript: str, count: int) -> List[Dict]:
        """Generate simple clips if AI fails"""
        logger.warning("Using fallback moment generation")
        # Split video into equal segments
        words = transcript.split()
        words_per_clip = len(words) // count
        
        moments = []
        for i in range(count):
            start = i * 30  # 30 seconds apart
            moments.append({
                "start_time": start,
                "end_time": start + 20,
                "duration": 20,
                "description": f"Clip {i+1}",
                "score": 50
            })
        
        return moments


# Example usage
if __name__ == "__main__":
    import asyncio
    
    async def test():
        agent = ClipperAgent()
        
        video_path = "/tmp/test_video.mp4"
        transcript = "This is a test transcript about productivity hacks..."
        
        clips = await agent.generate_clips(video_path, transcript, target_clips=10)
        
        print(f"Generated {len(clips)} clips:")
        for clip in clips:
            print(f"\n- {clip['description']}")
            print(f"  Time: {clip['start_time']:.1f}s - {clip['end_time']:.1f}s")
            print(f"  Score: {clip['score']}/100")
    
    # asyncio.run(test())
    print("Clipper agent ready")