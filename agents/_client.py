"""Shared model call wrapper used by every agent in this package.

Talks to the local OpenAI-compatible gateway (ANTHROPIC_BASE_URL) using the
ANTHROPIC_API_KEY. On a rate limit it retries briefly, and on any other API
hiccup it returns a safe fallback payload so the demo degrades gracefully
instead of throwing a 500.
"""

import json
import os
import re
import time
from pathlib import Path

import httpx

MODEL = "cc/claude-haiku-4-5-20251001"
DEFAULT_BASE_URL = "http://localhost:20128"


def _read_env_file() -> dict:
    env_path = Path(__file__).resolve().parent.parent / ".env"
    values: dict = {}
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            if "=" in line and not line.strip().startswith("#"):
                k, v = line.split("=", 1)
                values[k.strip()] = v.strip().strip('"').strip("'")
    return values


def _get_config() -> tuple[str | None, str]:
    """Return (api_key, base_url) from environment, falling back to a local .env."""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    base_url = os.environ.get("ANTHROPIC_BASE_URL")
    if not api_key or not base_url:
        file_env = _read_env_file()
        api_key = api_key or file_env.get("ANTHROPIC_API_KEY")
        base_url = base_url or file_env.get("ANTHROPIC_BASE_URL")
    return api_key, (base_url or DEFAULT_BASE_URL).rstrip("/")


def _content_from_response(resp: "httpx.Response") -> str:
    """Extract the assistant text from either a plain JSON completion or an
    SSE (streamed) chat.completion.chunk response."""
    body = resp.text.strip()
    if not body.startswith("data:"):
        data = resp.json()
        return data["choices"][0]["message"]["content"]

    # Server-Sent Events: concatenate the delta.content pieces.
    parts: list[str] = []
    for line in body.splitlines():
        line = line.strip()
        if not line.startswith("data:"):
            continue
        chunk = line[len("data:"):].strip()
        if not chunk or chunk == "[DONE]":
            continue
        try:
            obj = json.loads(chunk)
        except json.JSONDecodeError:
            continue
        for choice in obj.get("choices", []):
            piece = (choice.get("delta") or {}).get("content")
            if not piece:
                msg = choice.get("message") or {}
                piece = msg.get("content")
            if piece:
                parts.append(piece)
    return "".join(parts)


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
        "reasoning": "Demo fallback because the AI service is temporarily unavailable.",
        "draft_reply": "I'm currently unable to generate a tailored response because the AI service is temporarily unavailable. Please try again shortly.",
        "kb_sources": [],
        "confidence": "low",
        "score": 40,
        "status": "approved",
        "feedback": "Fallback response used because the AI service is unavailable.",
        "final_reply": "I'm currently unable to generate a tailored response because the AI service is temporarily unavailable. Please try again shortly.",
    }


def call_agent(system_prompt: str, user_content: str, max_tokens: int = 700) -> dict:
    """Call the model with a system prompt + user content, return parsed JSON.

    Retries on a rate limit with a short backoff, then falls back to a canned
    payload so a single 429 never breaks the whole chain.
    """
    api_key, base_url = _get_config()
    if not api_key:
        return _fallback_payload()

    payload = {
        "model": MODEL,
        "max_tokens": max_tokens,
        "temperature": 0,
        "stream": False,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content},
        ],
    }
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    url = f"{base_url}/v1/chat/completions"

    for attempt in range(3):
        try:
            resp = httpx.post(url, headers=headers, json=payload, timeout=60)
            if resp.status_code == 429:
                if attempt < 2:
                    time.sleep(2 * (attempt + 1))
                    continue
                return _fallback_payload()
            resp.raise_for_status()
            raw_text = _content_from_response(resp)
            return _extract_json(raw_text)
        except httpx.HTTPStatusError as err:
            if err.response is not None and err.response.status_code == 429 and attempt < 2:
                time.sleep(2 * (attempt + 1))
                continue
            return _fallback_payload()
        except Exception:  # noqa: BLE001 - any API/parse issue degrades gracefully
            return _fallback_payload()

    return _fallback_payload()
