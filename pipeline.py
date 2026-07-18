"""
Orchestration for The Inbox That Runs Itself.

process_ticket() runs the Triage agent first, then branches:
  - reply_needed tickets go through Specialist -> Reviewer
  - no_reply tickets are held for the end-of-day Digest agent

Returns a result dict with a "trace" containing one step per agent call,
in the order they actually ran, so a UI can render the chain progressively.
"""

from agents import triage_ticket, draft_reply, review_reply


def process_ticket(ticket: dict) -> dict:
    """Run the full agent chain for a single ticket. Returns the enriched
    ticket plus a trace of every agent step that ran."""
    trace_steps = []

    triage_result = triage_ticket(ticket)
    trace_steps.append({"agent": "triage", "output": triage_result})

    tag = triage_result.get("tag", "other")
    reply_needed = triage_result.get("reply_needed", True)
    priority = triage_result.get("priority", "medium")

    result = {
        "ticket_id": ticket["id"],
        "tag": tag,
        "priority": priority,
        "reply_needed": reply_needed,
        "status": "held_for_digest" if not reply_needed else "in_progress",
        "draft_reply": None,
        "final_reply": None,
        "score": None,
        "trace": {"steps": trace_steps},
    }

    if not reply_needed:
        return result

    draft = draft_reply(ticket, tag)
    trace_steps.append({"agent": "specialist", "output": draft})
    result["draft_reply"] = draft.get("draft_reply")
    result["status"] = "drafted"

    review = review_reply(ticket, draft)
    trace_steps.append({"agent": "reviewer", "output": review})
    result["final_reply"] = review.get("final_reply")
    result["score"] = review.get("score")
    result["status"] = review.get("status", "approved")

    return result
