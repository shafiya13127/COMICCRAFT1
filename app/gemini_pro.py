"""
Optional second-stage writer.

The main ComicCraft flow uses Gemini Flash
for text-only comic generation.
"""

from app.gemini_flash import generate_comic


__all__ = [
    "generate_comic"
]