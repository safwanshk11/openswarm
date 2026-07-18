"""Specialist agent: drafts a reply grounded in the knowledge base for the ticket's tag."""

import os

from ._client import call_agent

KB_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "kb")

TAG_TO_KB_FILE = {
    "billing": "01-billing-and-plans.md",
    "sync": "02-sync-and-upload-issues.md",
    "sharing": "03-sharing-and-permissions.md",
    "account_security": "04-account-and-security.md",
    "api_integration": "05-api-and-integrations.md",
}

SYSTEM_PROMPT = """You are the Specialist agent for Loomly Cloud customer support. \
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
    result = call_agent(SYSTEM_PROMPT, user_content, max_tokens=500)
    if kb_filename and not result.get("kb_sources"):
        result["kb_sources"] = [kb_filename]
    return result
