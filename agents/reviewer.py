"""Reviewer agent: quality-checks a Specialist draft before it goes out."""

from ._client import call_agent

SYSTEM_PROMPT = """You are the Reviewer agent for Loomly Cloud customer support. \
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
    result = call_agent(SYSTEM_PROMPT, user_content, max_tokens=500)
    if "score" in result:
        result["score"] = max(0, min(100, int(result["score"])))
    if result.get("status") not in ("approved", "needs_revision"):
        result["status"] = "approved" if result.get("score", 0) >= 75 else "needs_revision"
    return result
