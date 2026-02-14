from anthropic import Anthropic
from app.config import settings
from typing import List
import logging

logger = logging.getLogger(__name__)


class HookGeneratorAgent:
    """
    AI agent that generates viral TikTok hooks
    
    Analyzes video transcript and generates 10 variations of viral opening hooks
    that stop scrollers and drive engagement.
    """
    
    def __init__(self):
        self.client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.model = "claude-sonnet-4-20250514"
    
    async def generate_hooks(self, transcript: str, video_topic: str = None) -> List[str]:
        """
        Generate 10 viral hook variations
        
        Args:
            transcript: Full video transcript
            video_topic: Optional topic/niche hint
            
        Returns:
            List of 10 viral hook variations
        """
        try:
            prompt = self._build_prompt(transcript, video_topic)
            
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                temperature=0.9,  # Higher creativity for viral hooks
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            hooks = self._parse_hooks(response.content[0].text)
            logger.info(f"Generated {len(hooks)} viral hooks")
            return hooks
            
        except Exception as e:
            logger.error(f"Hook generation failed: {e}")
            return self._fallback_hooks(transcript)
    
    def _build_prompt(self, transcript: str, video_topic: str = None) -> str:
        """Build the AI prompt for hook generation"""
        
        topic_context = f"Video topic/niche: {video_topic}\n\n" if video_topic else ""
        
        prompt = f"""You are an expert TikTok content strategist who creates viral hooks.

{topic_context}Video transcript:
{transcript[:1000]}  

Your task: Generate 10 DIFFERENT viral hook variations for this TikTok video.

VIRAL HOOK PRINCIPLES:
1. Stop the scroll in first 3 seconds
2. Create curiosity gap ("you won't believe...")
3. Promise value or revelation
4. Use pattern interrupts
5. Emotional triggers (shock, curiosity, FOMO)
6. Speak directly to target audience

HOOK PATTERNS THAT WORK:
- "Wait until you hear this..."
- "This is actually insane..."
- "Nobody is talking about this..."
- "POV: You just discovered..."
- "Stop scrolling if you..."
- "As a [niche], this shocked me..."
- "Red flag if you don't know this..."
- "I can't believe I'm about to say this..."
- "The [industry] doesn't want you to know..."
- "[Number] [timeframe] and here's what happened..."

Generate 10 UNIQUE hooks. Each must:
- Be 5-15 words max
- Match the video's content/tone
- Use different patterns (don't repeat formulas)
- Sound natural for TikTok

Format as numbered list:
1. [hook]
2. [hook]
...
10. [hook]

DO NOT include explanations, just the hooks."""

        return prompt
    
    def _parse_hooks(self, response_text: str) -> List[str]:
        """Parse hooks from AI response"""
        hooks = []
        lines = response_text.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            # Match numbered format: "1. hook text" or "1) hook text"
            if line and (line[0].isdigit() or line.startswith('-')):
                # Remove number and cleanup
                hook = line.split('.', 1)[-1].split(')', 1)[-1].strip()
                hook = hook.strip('"\'')  # Remove quotes
                if hook:
                    hooks.append(hook)
        
        return hooks[:10]  # Max 10 hooks
    
    def _fallback_hooks(self, transcript: str) -> List[str]:
        """Fallback hooks if AI fails"""
        first_sentence = transcript.split('.')[0][:50]
        return [
            f"Wait until you hear this...",
            f"This is actually insane...",
            f"You need to know this...",
            f"Stop scrolling - this matters...",
            f"I can't believe this..."
        ]


# Example usage
if __name__ == "__main__":
    import asyncio
    
    async def test():
        agent = HookGeneratorAgent()
        
        transcript = """
        Hey everyone! So I just discovered this productivity hack that literally 
        changed my entire workflow. I used to spend 6 hours a day editing videos 
        and now it takes me 30 minutes. Let me show you how...
        """
        
        hooks = await agent.generate_hooks(transcript, "productivity tips")
        
        print("Generated Viral Hooks:")
        for i, hook in enumerate(hooks, 1):
            print(f"{i}. {hook}")
    
    asyncio.run(test())