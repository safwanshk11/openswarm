"""Agent definitions for The Inbox That Runs Itself.

Each agent lives in its own module and calls the Anthropic API with its own
system prompt, returning strict JSON matching a documented schema. No shared
state between agents, no classes, just functions the pipeline chains together.
"""

from .triage import triage_ticket
from .specialist import draft_reply
from .reviewer import review_reply
from .digest import build_digest

__all__ = ["triage_ticket", "draft_reply", "review_reply", "build_digest"]
