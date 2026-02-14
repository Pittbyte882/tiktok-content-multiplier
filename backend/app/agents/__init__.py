# app/agents/__init__.py
from .transcriber import TranscriberAgent
from .hook_generator import HookGeneratorAgent
from .caption_writer import CaptionWriterAgent  # ← Changed from CaptionGeneratorAgent
from .clipper import ClipperAgent

__all__ = [
    'TranscriberAgent',
    'HookGeneratorAgent', 
    'CaptionWriterAgent',  # ← Changed
    'ClipperAgent'
]