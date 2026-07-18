"""Shared Gemini call wrapper used by every agent in this package."""

import json
import os
import re
from pathlib import Path

import google.generativeai as genai
from google.api_core import exceptions as google_exceptions

MODEL = "gemini-2.0-flash"

_client = genai.GenerativeModel(MODEL)


def _get_api_key() -> str | None:
    """Read the Gemini API key from the environment or a local .env file."""
    if os.environ.get("GEMINI_API_KEY"):
        return os.environ["GEMINI_API_KEY"]

    env_path = Path(__file__).resolve().parent.parent / ".env"
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            if line.startswith("GEMINI_API_KEY="):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    return None


def _extract_json(text: str) -> dict:
    """Pull a JSON object out of a model response, tolerating code fences
    or stray prose around it."""
    text = text.strip()
    fence_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if fence_match:
        text = fence_match.group(1)
    else:
        brace_match = re.search(r"\{.*\}", text, re.DOTALL)
        if brace_match:
            text = brace_match.group(0)
    return json.loads(text)


def _fallback_payload() -> dict:
    return {
        "tag": "other",
        "reply_needed": True,
        "priority": "medium",
        "reasoning": "Demo fallback because the Gemini API quota is currently unavailable.",
        "draft_reply": "I’m currently unable to generate a tailored response because the AI service is temporarily unavailable. Please try again shortly.",
        "kb_sources": [],
        "confidence": "low",
        "score": 40,
        "status": "approved",
        "feedback": "Fallback response used because the AI service is unavailable.",
        "final_reply": "I’m currently unable to generate a tailored response because the AI service is temporarily unavailable. Please try again shortly.",
    }


def call_agent(system_prompt: str, user_content: str, max_tokens: int = 700) -> dict:
    """Call the Gemini model with a system prompt + user content, return parsed JSON."""
    api_key = _get_api_key()
    if not api_key:
        return _fallback_payload()

    try:
        genai.configure(api_key=api_key)
        response = _client.generate_content(
            [
                {"role": "user", "parts": [f"System prompt:\n{system_prompt}\n\nUser content:\n{user_content}"]}
            ],
            generation_config={"max_output_tokens": max_tokens, "temperature": 0},
        )
        raw_text = response.text
        return _extract_json(raw_text)
    except google_exceptions.ResourceExhausted:
        return _fallback_payload()
    except Exception:
        return _fallback_payload()
