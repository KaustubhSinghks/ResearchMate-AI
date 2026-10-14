import json
from typing import Any

from google import genai
from google.genai import types

from app.core.config import get_settings

_client: genai.Client | None = None


def _get_client() -> genai.Client:
    global _client
    if _client is None:
        _client = genai.Client(api_key=get_settings().gemini_api_key)
    return _client


def generate_text(system: str, user: str, max_tokens: int = 1500) -> str:
    """Plain-text Gemini completion, used for summaries, chat answers, comparisons, etc."""
    settings = get_settings()
    response = _get_client().models.generate_content(
        model=settings.gemini_model,
        contents=user,
        config=types.GenerateContentConfig(
            system_instruction=system,
            max_output_tokens=max_tokens,
            # Thinking tokens count against max_output_tokens and can silently eat the
            # whole budget before any visible text is produced; these tasks don't need deep reasoning.
            thinking_config=types.ThinkingConfig(thinking_level=types.ThinkingLevel.MINIMAL),
        ),
    )
    return response.text or ""


def generate_structured(
    system: str,
    user: str,
    tool_description: str,
    input_schema: dict[str, Any],
    max_tokens: int = 2000,
) -> dict[str, Any]:
    """Force Gemini to respond with JSON matching input_schema, for reliable structured extraction."""
    settings = get_settings()
    response = _get_client().models.generate_content(
        model=settings.gemini_model,
        contents=user,
        config=types.GenerateContentConfig(
            system_instruction=f"{system}\n\n{tool_description}",
            max_output_tokens=max_tokens,
            response_mime_type="application/json",
            response_json_schema=input_schema,
            thinking_config=types.ThinkingConfig(thinking_level=types.ThinkingLevel.MINIMAL),
        ),
    )

    if not response.text:
        raise ValueError("Gemini did not return a structured response")

    return json.loads(response.text)
