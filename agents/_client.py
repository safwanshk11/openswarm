"""Shared Anthropic call wrapper used by every agent in this package."""

import json
import os
import re

from anthropic import Anthropic

MODEL = "cc/claude-haiku-4-5-20251001"

_client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))


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


def call_agent(system_prompt: str, user_content: str, max_tokens: int = 700) -> dict:
    """Call the model with a system prompt + user content, return parsed JSON."""
    response = _client.messages.create(
        model=MODEL,
        max_tokens=max_tokens,
        system=system_prompt,
        messages=[{"role": "user", "content": user_content}],
    )
    raw_text = "".join(
        block.text for block in response.content if block.type == "text"
    )
    return _extract_json(raw_text)
