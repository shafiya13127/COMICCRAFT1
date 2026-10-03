import json
import time

from google import genai
from google.genai import types

from app.config import get_settings
from app.schemas import ComicResponse


class GeminiServiceError(Exception):
    pass


def create_client():
    settings = get_settings()

    if not settings.gemini_api_key:
        raise GeminiServiceError(
            "GEMINI_API_KEY is missing from the .env file."
        )

    return genai.Client(
        api_key=settings.gemini_api_key
    )


def generate_comic(
    prompt: str,
    style: str,
    language: str,
    panels: int
) -> ComicResponse:

    settings = get_settings()
    client = create_client()

    instruction = f"""
You are ComicCraft AI, a professional comic story writer.

Create a complete text-only comic story.

USER STORY IDEA:
{prompt}

COMIC STYLE:
{style}

LANGUAGE:
{language}

NUMBER OF PANELS:
{panels}

RULES:

1. Create exactly {panels} panels.
2. Create a short and interesting comic title.
3. List the main characters.
4. Every panel must contain:
   - panel
   - title
   - scene_description
   - narration
   - dialogue
5. Dialogue must be a JSON array of strings.
6. Each dialogue line must start with the character name.
7. The story must continue naturally from panel to panel.
8. Give the story a clear beginning, middle and ending.
9. Keep the story family-friendly.
10. Write everything in {language}.
11. Do NOT generate images.
12. Do NOT create image prompts.
13. Return ONLY valid JSON.
14. Do not use Markdown.
15. Do not put ``` around the JSON.

Use exactly this JSON structure:

{{
  "title": "Comic title",
  "characters": [
    "Character 1",
    "Character 2"
  ],
  "panels": [
    {{
      "panel": 1,
      "title": "Panel title",
      "scene_description": "Description of the scene",
      "narration": "Narration text",
      "dialogue": [
        "Character 1: Dialogue",
        "Character 2: Dialogue"
      ]
    }}
  ],
  "style": "{style}",
  "language": "{language}"
}}
"""

    last_error = None

    # Try up to 5 times for temporary Gemini server errors.
    for attempt in range(5):

        try:
            response = client.models.generate_content(
                model=settings.gemini_model,
                contents=instruction,
                config=types.GenerateContentConfig(
                    temperature=0.8,
                    max_output_tokens=3500,
                    response_mime_type="application/json"
                )
            )

            if not response.text:
                raise GeminiServiceError(
                    "Gemini returned an empty response."
                )

            # Convert Gemini's JSON text into Python data.
            try:
                data = json.loads(response.text)
            except json.JSONDecodeError as exc:
                raise GeminiServiceError(
                    f"Gemini returned invalid JSON: {exc}"
                )

            # Validate the generated comic.
            result = ComicResponse.model_validate(data)

            # Make sure Gemini created the requested number of panels.
            if len(result.panels) != panels:
                raise GeminiServiceError(
                    f"Gemini returned {len(result.panels)} panels "
                    f"instead of {panels}."
                )

            return result

        except Exception as exc:

            last_error = exc
            message = str(exc).lower()

            retryable = any(
                word in message
                for word in [
                    "503",
                    "429",
                    "unavailable",
                    "overloaded",
                    "resource exhausted",
                    "timeout",
                    "high demand"
                ]
            )

            if retryable and attempt < 4:

                wait_seconds = 3 * (2 ** attempt)

                print(
                    f"Gemini temporarily unavailable. "
                    f"Retrying in {wait_seconds} seconds..."
                )

                time.sleep(wait_seconds)
                continue

            break

    raise GeminiServiceError(
        "Gemini is temporarily unavailable. "
        "Please try again after a short while. "
        f"Technical detail: {last_error}"
    )