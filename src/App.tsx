import { useCallback, useEffect, useRef, useState } from "react";
import Header from "./components/Header";
import SortingTray from "./components/SortingTray";
import DigestPanel from "./components/DigestPanel";
import TraceOverlay from "./components/TraceOverlay";
import type { Digest, ProcessResult, Ticket, TraceAgent, TraceLine } from "./types";
import demoTicketsData from "../tickets.json";

const API_BASE = "http://127.0.0.1:8000";
const fallbackTickets: Ticket[] = (demoTicketsData as Array<Partial<Ticket>>).map((ticket) => ({
  ...ticket,
  status: "unprocessed",
})) as Ticket[];

function sleep(ms: number) {
  return new Promise((r) => setTimeout(r, ms));
}

export default function App() {
  const [tickets, setTickets] = useState<Ticket[]>([]);
  const [digest, setDigest] = useState<Digest | null>(null);
  const [traceLines, setTraceLines] = useState<TraceLine[]>([]);
  const [traceOpen, setTraceOpen] = useState(false);
  const [processDisabled, setProcessDisabled] = useState(false);
  const [processLabel, setProcessLabel] = useState("Process next ticket");
  const [voicemailDisabled, setVoicemailDisabled] = useState(false);
  const [flashIds, setFlashIds] = useState<Set<string>>(new Set());

  const ticketsRef = useRef<Ticket[]>([]);
  ticketsRef.current = tickets;
  const traceIdRef = useRef(0);

  const logTrace = useCallback((agent: TraceAgent, text: string) => {
    const time = new Date().toLocaleTimeString([], { hour12: false });
    traceIdRef.current += 1;
    setTraceLines((prev) => [...prev, { id: traceIdRef.current, time, agent, text }]);
  }, []);

  const flash = useCallback((id: string) => {
    setFlashIds((prev) => new Set(prev).add(id));
    setTimeout(() => {
      setFlashIds((prev) => {
        const next = new Set(prev);
        next.delete(id);
        return next;
      });
    }, 1100);
  }, []);

  const upsertTicket = useCallback((updated: Ticket) => {
    setTickets((prev) => {
      const idx = prev.findIndex((t) => t.id === updated.id);
      if (idx === -1) return [...prev, updated];
      const next = [...prev];
      next[idx] = { ...next[idx], ...updated };
      return next;
    });
  }, []);

  const loadTickets = useCallback(async () => {
    try {
      const res = await fetch(`${API_BASE}/tickets`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data: Ticket[] = await res.json();
      setTickets(data);
    } catch {
      setTickets(fallbackTickets);
    }
  }, []);

  const loadDigest = useCallback(async () => {
    try {
      const res = await fetch(`${API_BASE}/digest`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data: Digest = await res.json();
      setDigest(data);
    } catch {
      setDigest({
        summary: "Demo digest unavailable right now, but the inbox is still populated with sample tickets.",
        highlights: [],
        ticket_count: fallbackTickets.length,
      });
    }
  }, []);

  const revealTrace = useCallback(
    async (ticket: Ticket, result: ProcessResult) => {
      const steps = result.trace?.steps || [];

      upsertTicket({ ...ticket, status: "in_progress" });

      for (const step of steps) {
        await sleep(550);
        if (step.agent === "triage") {
          const { output } = step;
          logTrace(
            "triage",
            `tag=${output.tag} priority=${output.priority} reply_needed=${output.reply_needed} — ${
              output.reasoning || ""
            }`
          );
          upsertTicket({
            ...ticket,
            tag: output.tag,
            priority: output.priority,
            reply_needed: output.reply_needed,
            status: output.reply_needed ? "in_progress" : "held_for_digest",
          });
        } else if (step.agent === "specialist") {
          const { output } = step;
          logTrace("specialist", `confidence=${output.confidence} kb_sources=${(output.kb_sources || []).join(",")}`);
          upsertTicket({ ...ticket, draft_reply: output.draft_reply, status: "in_progress" });
        } else if (step.agent === "reviewer") {
          const { output } = step;
          logTrace("reviewer", `score=${output.score} status=${output.status} — ${output.feedback || ""}`);
          upsertTicket({ ...ticket, final_reply: output.final_reply, score: output.score, status: output.status });
        }
      }

      // Reconcile with whatever the backend ultimately settled on.
      upsertTicket({
        ...ticket,
        status: result.status,
        tag: result.tag,
        priority: result.priority,
        draft_reply: result.draft_reply,
        final_reply: result.final_reply,
        score: result.score,
      });
      flash(ticket.id);
    },
    [upsertTicket, logTrace, flash]
  );

  const nextUnprocessedTicket = useCallback(() => {
    return ticketsRef.current.find((t) => t.status === "unprocessed");
  }, []);

  const processNextTicket = useCallback(async () => {
    const ticket = nextUnprocessedTicket();
    if (!ticket) {
      logTrace("system", "no unprocessed tickets remaining");
      setProcessDisabled(true);
      setProcessLabel("All tickets processed");
      return;
    }

    setProcessDisabled(true);
    logTrace("system", `processing ${ticket.id}: "${ticket.subject}"`);

    try {
      const res = await fetch(`${API_BASE}/process/${encodeURIComponent(ticket.id)}`, { method: "POST" });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const result: ProcessResult = await res.json();
      await revealTrace(ticket, result);
      await loadDigest();
    } catch (err) {
      logTrace("system", `error processing ${ticket.id}: ${(err as Error).message}`);
    } finally {
      const remaining = nextUnprocessedTicket();
      setProcessDisabled(!remaining);
      if (!remaining) setProcessLabel("All tickets processed");
    }
  }, [nextUnprocessedTicket, logTrace, revealTrace, loadDigest]);

  const playVoicemail = useCallback(async () => {
    setVoicemailDisabled(true);
    logTrace("system", "transcribing voicemail: demo_voicemail_1…");

    try {
      const res = await fetch(`${API_BASE}/process-voicemail/demo_voicemail_1`, { method: "POST" });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const result: ProcessResult = await res.json();

      // Insert the transcribed ticket into the tray immediately, before the
      // agent chain runs, so it visibly "arrives" from the voicemail.
      const placeholder: Ticket = {
        id: result.id,
        subject: result.subject,
        customer: result.customer,
        status: "in_progress",
        tag: null,
        draft_reply: null,
        final_reply: null,
        score: null,
        reply_needed: null,
      };
      setTickets((prev) => [...prev, placeholder]);
      flash(placeholder.id);
      logTrace("system", `voicemail transcribed → new ticket ${result.id}: "${result.subject}"`);

      await revealTrace(placeholder, result);
      await loadDigest();
    } catch (err) {
      logTrace("system", `error processing voicemail: ${(err as Error).message}`);
    } finally {
      setVoicemailDisabled(false);
    }
  }, [logTrace, revealTrace, loadDigest, flash]);

  useEffect(() => {
    (async () => {
      logTrace("system", "loading inbox…");
      try {
        await fetch(`${API_BASE}/reset`, { method: "POST" });
      } catch {
        // Ignore reset failures and continue loading the existing data.
      }
      await loadTickets();
      await loadDigest();
      logTrace("system", "ready");
    })();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <>
      <Header
        onProcessNext={processNextTicket}
        onPlayVoicemail={playVoicemail}
        processDisabled={processDisabled}
        processLabel={processLabel}
        voicemailDisabled={voicemailDisabled}
      />
      <main className="grid grid-cols-[1fr_360px] items-start stack:grid-cols-1">
        <SortingTray tickets={tickets} flashIds={flashIds} />
        <DigestPanel digest={digest} onOpenTrace={() => setTraceOpen(true)} />
      </main>
      <TraceOverlay open={traceOpen} lines={traceLines} onClose={() => setTraceOpen(false)} />
    </>
  );
}
