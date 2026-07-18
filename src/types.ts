export type TicketStatus =
  | "unprocessed"
  | "in_progress"
  | "approved"
  | "needs_revision"
  | "held_for_digest";

export interface Ticket {
  id: string;
  subject: string;
  customer?: string;
  priority?: string | null;
  tag?: string | null;
  reply_needed?: boolean | null;
  draft_reply?: string | null;
  final_reply?: string | null;
  score?: number | null;
  status: TicketStatus | string;
  [key: string]: unknown;
}

export interface TraceStepTriage {
  agent: "triage";
  output: {
    tag: string;
    priority: string;
    reply_needed: boolean;
    reasoning?: string;
  };
}

export interface TraceStepSpecialist {
  agent: "specialist";
  output: {
    draft_reply: string;
    confidence?: string | number;
    kb_sources?: string[];
  };
}

export interface TraceStepReviewer {
  agent: "reviewer";
  output: {
    final_reply: string;
    score: number;
    status: TicketStatus | string;
    feedback?: string;
  };
}

export type TraceStep = TraceStepTriage | TraceStepSpecialist | TraceStepReviewer;

export interface ProcessResult extends Ticket {
  trace?: { steps: TraceStep[] };
}

export interface Digest {
  summary?: string;
  highlights?: string[];
  ticket_count: number;
}

export type TraceAgent = "triage" | "specialist" | "reviewer" | "digest" | "system";

export interface TraceLine {
  id: number;
  time: string;
  agent: TraceAgent;
  text: string;
}
