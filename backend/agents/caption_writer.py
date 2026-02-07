from anthropic import Anthropic
from app.config import settings
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)


class CaptionWriterAgent:
    """
    AI agent that generates TikTok captions with hashtags
    
    Creates engaging captions optimized for TikTok algorithm with
    strategic hashtag combinations (trending + niche + growing).
    """
    
    def __init__(self):
        self.client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.model = "claude-sonnet-4-20250514"
    
    async def generate_captions(self, transcript: str, video_topic: str = None, hook: str = None) -> List[Dict]:
        """
        Generate 5 caption variations with hashtags
        
        Args:
            transcript: Full video transcript
            video_topic: Optional topic/niche
            hook: Optional viral hook to incorporate
            
        Returns:
            List of caption dicts with:
                - caption: Main caption text
                - hashtags: List of hashtags
                - character_count: Total length
        """
        try:
            prompt = self._build_prompt(transcript, video_topic, hook)
            
            response = self.client.messages.create(
                model=self.model,
                max_tokens=3000,
                temperature=0.8,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            captions = self._parse_captions(response.content[0].text)
            logger.info(f"Generated {len(captions)} caption variations")
            return captions
            
        except Exception as e:
            logger.error(f"Caption generation failed: {e}")
            return self._fallback_captions(transcript)
    
    def _build_prompt(self, transcript: str, video_topic: str = None, hook: str = None) -> str:
        """Build the AI prompt for caption generation"""
        
        topic_context = f"Video topic/niche: {video_topic}\n" if video_topic else ""
        hook_context = f"Viral hook: {hook}\n" if hook else ""
        
        prompt = f"""You are an expert TikTok caption writer and hashtag strategist.

{topic_context}{hook_context}
Video transcript:
{transcript[:800]}

Generate 5 DIFFERENT caption variations optimized for TikTok.

CAPTION BEST PRACTICES:
1. Start strong (use hook if provided, or create compelling opening)
2. Keep it conversational and authentic
3. Use emojis strategically (2-4 per caption)
4. Include call-to-action (save, share, follow, comment)
5. Create FOMO or curiosity
6. Max 150 characters (TikTok optimal length)
7. Use line breaks for readability

HASHTAG STRATEGY (10-15 hashtags per caption):
- Mix of trending (#fyp, #foryou, #viral)
- Niche-specific (relevant to content)
- Growing hashtags (moderate volume, less competition)
- Community tags (target audience)

Format each caption EXACTLY like this:

---CAPTION 1---
[Caption text with emojis and line breaks]

#hashtag1 #hashtag2 #hashtag3 #hashtag4 #hashtag5 #hashtag6 #hashtag7 #hashtag8 #hashtag9 #hashtag10

---CAPTION 2---
[Different caption approach]

#hashtag1 #hashtag2 #hashtag3 #hashtag4 #hashtag5 #hashtag6 #hashtag7 #hashtag8 #hashtag9 #hashtag10

[Continue for 5 captions]

Make each caption UNIQUE - different angle, tone, or CTA."""

        return prompt
    
    def _parse_captions(self, response_text: str) -> List[Dict]:
        """Parse captions from AI response"""
        captions = []
        
        # Split by caption markers
        sections = response_text.split('---CAPTION')
        
        for section in sections[1:]:  # Skip first empty section
            try:
                # Extract caption number and content
                parts = section.split('---', 1)
                if len(parts) < 2:
                    continue
                    
                content = parts[1].strip()
                
                # Split caption text and hashtags
                lines = content.split('\n')
                
                caption_text = []
                hashtags = []
                
                for line in lines:
                    line = line.strip()
                    if line.startswith('#'):
                        # Extract hashtags
                        tags = [tag.strip() for tag in line.split() if tag.startswith('#')]
                        hashtags.extend(tags)
                    elif line:
                        caption_text.append(line)
                
                if caption_text:
                    full_caption = '\n'.join(caption_text)
                    
                    captions.append({
                        "caption": full_caption,
                        "hashtags": hashtags[:15],  # Max 15 hashtags
                        "character_count": len(full_caption) + len(' '.join(hashtags))
                    })
                    
            except Exception as e:
                logger.warning(f"Failed to parse caption section: {e}")
                continue
        
        return captions[:5]  # Max 5 captions
    
    def _fallback_captions(self, transcript: str) -> List[Dict]:
        """Fallback captions if AI fails"""
        snippet = transcript[:100]
        
        return [
            {
                "caption": f"{snippet}... 💯\n\nWhat do you think? Let me know! 👇",
                "hashtags": ["#fyp", "#foryou", "#viral", "#tiktoktips"],
                "character_count": 150
            }
        ]


# Example usage
if __name__ == "__main__":
    import asyncio
    
    async def test():
        agent = CaptionWriterAgent()
        
        transcript = """
        Hey everyone! Today I'm sharing my top 3 productivity hacks that 
        literally changed my life. First one is game-changing...
        """
        
        captions = await agent.generate_captions(
            transcript,
            video_topic="productivity tips",
            hook="Wait until you see hack #3..."
        )
        
        print("Generated Captions:\n")
        for i, cap in enumerate(captions, 1):
            print(f"--- Caption {i} ({cap['character_count']} chars) ---")
            print(cap['caption'])
            print(' '.join(cap['hashtags']))
            print()
    
    asyncio.run(test())