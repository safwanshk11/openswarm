"""
Agent definitions for The Inbox That Runs Itself.

Each agent is a plain function that calls the Anthropic API with its own
system prompt and returns strict JSON matching a documented schema.
No shared state, no classes, just functions the pipeline chains together.
"""

import json
import os
import re

from anthropic import Anthropic

MODEL = "cc/claude-haiku-4-5-20251001"

_client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

KB_DIR = os.path.join(os.path.dirname(__file__), "kb")

TAG_TO_KB_FILE = {
    "billing": "01-billing-and-plans.md",
    "sync": "02-sync-and-upload-issues.md",
    "sharing": "03-sharing-and-permissions.md",
    "account_security": "04-account-and-security.md",
    "api_integration": "05-api-and-integrations.md",
}

VALID_TAGS = [
    "billing",
    "sync",
    "sharing",
    "account_security",
    "api_integration",
    "feature_request",
    "positive_feedback",
    "other",
]


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


def _call(system_prompt: str, user_content: str, max_tokens: int = 700) -> dict:
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


# ---------------------------------------------------------------------------
# 1. Triage agent
# ---------------------------------------------------------------------------

TRIAGE_SYSTEM_PROMPT = """You are the Triage agent for a customer support inbox at Loomly Cloud, \
a cloud storage and file sync product.

Read the incoming ticket and classify it. Respond with ONLY a single JSON object, \
no prose, no markdown fences, matching exactly this schema:

{
  "tag": one of ["billing", "sync", "sharing", "account_security", "api_integration", "feature_request", "positive_feedback", "other"],
  "reply_needed": true or false,
  "priority": one of ["low", "medium", "high", "urgent"],
  "reasoning": a one-sentence explanation of the classification
}

Rules:
- "positive_feedback" and pure "feature_request" tickets with no blocking issue should have reply_needed=false \
(they get bundled into a daily digest instead of an individual reply).
- Every other category should have reply_needed=true.
- priority "urgent" is reserved for tickets describing an active lockout, data loss risk, or a hard deadline \
within 24 hours.
"""


def triage_ticket(ticket: dict) -> dict:
    """Classify a ticket. Returns dict with tag, reply_needed, priority, reasoning."""
    user_content = (
        f"Subject: {ticket['subject']}\n"
        f"Customer: {ticket['customer']}\n"
        f"Body: {ticket['body']}"
    )
    result = _call(TRIAGE_SYSTEM_PROMPT, user_content, max_tokens=300)
    if result.get("tag") not in VALID_TAGS:
        result["tag"] = "other"
    result["reply_needed"] = bool(result.get("reply_needed", True))
    return result


# ---------------------------------------------------------------------------
# 2. Specialist agent
# ---------------------------------------------------------------------------

SPECIALIST_SYSTEM_PROMPT = """You are the Specialist agent for Loomly Cloud customer support. \
You write draft replies to customers grounded strictly in the provided knowledge base excerpt. \
Do not invent policies, timelines, or numbers that aren't in the excerpt.

Respond with ONLY a single JSON object, no prose, no markdown fences, matching exactly this schema:

{
  "draft_reply": a complete, warm, concise reply to the customer (2-5 sentences, plain text, no markdown),
  "kb_sources": array of knowledge base filenames actually used,
  "confidence": one of ["low", "medium", "high"]
}

If the knowledge base excerpt does not cover the customer's issue, say so honestly in the draft \
and set confidence to "low" rather than guessing.
"""


def draft_reply(ticket: dict, tag: str) -> dict:
    """Draft a reply grounded in the KB doc matching this ticket's tag."""
    kb_filename = TAG_TO_KB_FILE.get(tag)
    kb_excerpt = "No knowledge base article matches this category."
    if kb_filename:
        kb_path = os.path.join(KB_DIR, kb_filename)
        if os.path.exists(kb_path):
            with open(kb_path, "r") as f:
                kb_excerpt = f.read()

    user_content = (
        f"Ticket category: {tag}\n"
        f"Customer: {ticket['customer']}\n"
        f"Subject: {ticket['subject']}\n"
        f"Body: {ticket['body']}\n\n"
        f"Knowledge base excerpt ({kb_filename or 'none'}):\n{kb_excerpt}"
    )
    result = _call(SPECIALIST_SYSTEM_PROMPT, user_content, max_tokens=500)
    if kb_filename and not result.get("kb_sources"):
        result["kb_sources"] = [kb_filename]
    return result


# ---------------------------------------------------------------------------
# 3. Reviewer agent
# ---------------------------------------------------------------------------

REVIEWER_SYSTEM_PROMPT = """You are the Reviewer agent for Loomly Cloud customer support. \
You quality-check a draft reply written by the Specialist agent before it goes out to a customer.

Score the draft on accuracy (does it match the knowledge base and not invent facts), tone \
(warm, professional, concise), and completeness (does it actually address the customer's issue).

Respond with ONLY a single JSON object, no prose, no markdown fences, matching exactly this schema:

{
  "score": integer from 0 to 100,
  "status": one of ["approved", "needs_revision"],
  "feedback": a one-sentence explanation of the score,
  "final_reply": the draft reply, lightly edited if needed for tone or clarity, otherwise unchanged
}

Use status "approved" for scores of 75 and above. Use "needs_revision" below that.
"""


def review_reply(ticket: dict, draft: dict) -> dict:
    """Score and finalize a specialist's draft reply."""
    user_content = (
        f"Customer issue: {ticket['subject']} - {ticket['body']}\n\n"
        f"Draft reply: {draft.get('draft_reply', '')}\n"
        f"Specialist confidence: {draft.get('confidence', 'unknown')}\n"
        f"KB sources used: {draft.get('kb_sources', [])}"
    )
    result = _call(REVIEWER_SYSTEM_PROMPT, user_content, max_tokens=500)
    if "score" in result:
        result["score"] = max(0, min(100, int(result["score"])))
    if result.get("status") not in ("approved", "needs_revision"):
        result["status"] = "approved" if result.get("score", 0) >= 75 else "needs_revision"
    return result


# ---------------------------------------------------------------------------
# 4. Digest agent
# ---------------------------------------------------------------------------

DIGEST_SYSTEM_PROMPT = """You are the Digest agent for Loomly Cloud customer support. \
You summarize a batch of tickets that did not need an individual reply (positive feedback, \
feature requests, low-priority notes) into a short daily digest for the support team lead.

Respond with ONLY a single JSON object, no prose, no markdown fences, matching exactly this schema:

{
  "summary": a 1-2 sentence overview of the batch,
  "highlights": array of short strings, one per ticket, each capturing the key point and customer name
}
"""


def build_digest(tickets: list) -> dict:
    """Summarize a batch of no-reply tickets into a digest."""
    if not tickets:
        return {"summary": "No tickets held for digest yet.", "highlights": []}

    lines = []
    for t in tickets:
        lines.append(
            f"- [{t.get('tag', 'other')}] {t['customer']}: {t['subject']} - {t['body']}"
        )
    user_content = "Tickets to summarize:\n" + "\n".join(lines)
    return _call(DIGEST_SYSTEM_PROMPT, user_content, max_tokens=600)
