"""Digest agent: summarizes tickets that didn't need an individual reply."""

from ._client import call_agent

SYSTEM_PROMPT = """You are the Digest agent for Loomly Cloud customer support. \
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
    return call_agent(SYSTEM_PROMPT, user_content, max_tokens=600)
