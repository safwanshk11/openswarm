"""
FastAPI backend for The Inbox That Runs Itself.

Endpoints:
  GET  /tickets                          - list all tickets with current processing state
  POST /process/{ticket_id}              - run the agent chain on one ticket
  POST /process-voicemail/{audio_label}  - transcribe a canned voicemail into a new ticket, then process it
  GET  /digest                           - build the daily digest for tickets held with no reply
"""

import json
import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from agents import build_digest
from pipeline import process_ticket

app = FastAPI(title="The Inbox That Runs Itself")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

TICKETS_PATH = os.path.join(os.path.dirname(__file__), "tickets.json")

# In-memory store: ticket_id -> merged {**original_ticket, **process_result}
_tickets_by_id: dict = {}
_ticket_order: list = []


def _load_tickets():
    with open(TICKETS_PATH, "r") as f:
        raw_tickets = json.load(f)
    for t in raw_tickets:
        _tickets_by_id[t["id"]] = {**t, "status": "unprocessed"}
        _ticket_order.append(t["id"])


_load_tickets()

# Canned voicemail transcripts, keyed by label, so the demo doesn't need real audio input.
VOICEMAIL_TRANSCRIPTS = {
    "demo_voicemail_1": {
        "subject": "Voicemail: can't access my team's shared drive",
        "customer": "Sam Whitfield",
        "email": "sam.whitfield@example.com",
        "body": (
            "Hi, this is Sam from the Whitfield team account. Our whole team lost access to "
            "the shared drive this morning, we're seeing a permission error when anyone tries "
            "to open it. We have a client call in an hour and really need this sorted. Please "
            "call me back or email as soon as you can."
        ),
    }
}


@app.get("/tickets")
def get_tickets():
    """Return all tickets in original order, each with its current processing state."""
    return [_tickets_by_id[tid] for tid in _ticket_order]


@app.post("/process/{ticket_id}")
def process(ticket_id: str):
    """Run the Triage -> (Specialist -> Reviewer | held) chain on one ticket."""
    ticket = _tickets_by_id.get(ticket_id)
    if ticket is None:
        raise HTTPException(status_code=404, detail=f"Ticket {ticket_id} not found")

    result = process_ticket(ticket)
    _tickets_by_id[ticket_id] = {**ticket, **result}
    return _tickets_by_id[ticket_id]


@app.post("/process-voicemail/{audio_label}")
def process_voicemail(audio_label: str):
    """Simulate transcribing a voicemail into a new ticket, add it to the inbox,
    then immediately run it through the agent chain."""
    transcript = VOICEMAIL_TRANSCRIPTS.get(audio_label)
    if transcript is None:
        raise HTTPException(status_code=404, detail=f"Voicemail {audio_label} not found")

    new_id = f"T-VM-{audio_label}"
    ticket = {
        "id": new_id,
        "subject": transcript["subject"],
        "customer": transcript["customer"],
        "email": transcript["email"],
        "channel": "voicemail",
        "body": transcript["body"],
        "created_at": None,
    }

    _tickets_by_id[new_id] = {**ticket, "status": "unprocessed"}
    if new_id not in _ticket_order:
        _ticket_order.append(new_id)

    result = process_ticket(ticket)
    _tickets_by_id[new_id] = {**ticket, **result}
    return _tickets_by_id[new_id]


@app.get("/digest")
def get_digest():
    """Build a digest from every currently held (no-reply) ticket."""
    held_tickets = [
        t for t in (_tickets_by_id[tid] for tid in _ticket_order)
        if t.get("status") == "held_for_digest"
    ]
    digest = build_digest(held_tickets)
    return {
        "summary": digest.get("summary"),
        "highlights": digest.get("highlights", []),
        "ticket_count": len(held_tickets),
    }
