"""Triage agent: classifies incoming tickets before anything else runs."""

from ._client import call_agent

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

SYSTEM_PROMPT = """You are the Triage agent for a customer support inbox at Loomly Cloud, \
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
    result = call_agent(SYSTEM_PROMPT, user_content, max_tokens=300)
    if result.get("tag") not in VALID_TAGS:
        result["tag"] = "other"
    result["reply_needed"] = bool(result.get("reply_needed", True))
    return result
