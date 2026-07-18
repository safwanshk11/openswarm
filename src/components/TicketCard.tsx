import { useEffect, useRef, useState } from "react";
import type { Ticket } from "../types";
import StepTracker from "./StepTracker";

const STAMP_LABEL: Record<string, string> = {
  approved: "Approved",
  needs_revision: "Needs\nRevision",
  held_for_digest: "Held for\nDigest",
};

const STAMP_COLOR: Record<string, string> = {
  approved: "text-postal-green",
  needs_revision: "text-stamp-red",
  held_for_digest: "text-kraft",
};

function truncate(str: string | null | undefined, n: number) {
  if (!str) return "";
  return str.length > n ? str.slice(0, n - 1) + "…" : str;
}

interface TicketCardProps {
  ticket: Ticket;
  flash: boolean;
  isExpanded: boolean;
  onToggle: () => void;
}

export default function TicketCard({ ticket, flash, isExpanded, onToggle }: TicketCardProps) {
  const [flashKey, setFlashKey] = useState(0);
  const mounted = useRef(false);

  useEffect(() => {
    if (!mounted.current) {
      mounted.current = true;
      return;
    }
    if (flash) setFlashKey((k) => k + 1);
  }, [flash]);

  const tagHtml = ticket.tag ? (
    <span className="flex-none whitespace-nowrap rounded-full border border-rule px-2 py-[3px] font-mono text-[10.5px] uppercase tracking-wide text-ink-soft">
      {String(ticket.tag).replace(/_/g, " ")}
    </span>
  ) : null;

  let draftContent: React.ReactNode;
  if (ticket.reply_needed === false && ticket.status === "held_for_digest") {
    draftContent = (
      <span className="italic text-ink-soft">No reply needed &middot; bundled into today&rsquo;s digest.</span>
    );
  } else if (ticket.final_reply || ticket.draft_reply) {
    draftContent = truncate((ticket.final_reply as string) || (ticket.draft_reply as string), 150);
  } else if (ticket.status === "in_progress") {
    draftContent = (
      <span className="font-mono text-[11px] uppercase tracking-wide text-ink-soft">
        <span className="mr-1.5 inline-block h-1.5 w-1.5 animate-pulse rounded-full bg-slot-blue align-middle" />
        Drafting reply&hellip;
      </span>
    );
  } else {
    draftContent = <span className="italic text-ink-soft">Waiting in tray.</span>;
  }

  const stampLabel = STAMP_LABEL[ticket.status as string];
  const stampColor = STAMP_COLOR[ticket.status as string];

  function handleKeyDown(e: React.KeyboardEvent) {
    if (e.key === "Enter" || e.key === " ") {
      e.preventDefault();
      onToggle();
    }
  }

  return (
    <div
      key={flashKey}
      className={`relative flex overflow-hidden rounded border border-rule bg-paper-card shadow-card ${
        flashKey > 0 ? "animate-cardFlash" : ""
      }`}
    >
      <div className="stub-rail">
        <span className="font-mono text-xs font-semibold">{ticket.id}</span>
        <span className="font-mono text-[9px] uppercase tracking-wide text-ink-soft">
          {ticket.priority || ""}
        </span>
      </div>
      <div className="min-w-0 flex-1">
        <div
          role="button"
          tabIndex={0}
          aria-expanded={isExpanded}
          onClick={onToggle}
          onKeyDown={handleKeyDown}
          className="cursor-pointer p-3.5 px-[18px] transition-colors duration-150 hover:bg-paper-shade/40"
        >
          <div className="flex items-start justify-between gap-3">
            <div className="min-w-0">
              <div className="text-[14.5px] font-semibold leading-tight">{ticket.subject}</div>
              <div className="mt-0.5 text-[12.5px] text-ink-soft">{ticket.customer || ""}</div>
            </div>
            <div className="flex flex-none items-start gap-2">
              {tagHtml}
              <span
                aria-hidden="true"
                className={`mt-0.5 inline-block font-mono text-[11px] text-ink-soft transition-transform duration-200 ease-out ${
                  isExpanded ? "-rotate-180" : "rotate-0"
                }`}
              >
                ▼
              </span>
            </div>
          </div>
          <div className="mt-2.5 whitespace-pre-wrap text-[13px] leading-normal text-ink">{draftContent}</div>
          <div className="mt-3 flex items-center justify-between gap-3">
            <StepTracker ticket={ticket} />
            {ticket.score !== null && ticket.score !== undefined ? (
              <span className="font-mono text-xs text-ink-soft">
                Score <b className="text-[13px] text-ink">{ticket.score as number}</b>
              </span>
            ) : (
              <span />
            )}
          </div>
        </div>
        <div
          className="grid transition-[grid-template-rows] duration-300 ease-out"
          style={{ gridTemplateRows: isExpanded ? "1fr" : "0fr" }}
        >
          <div className="overflow-hidden">
            <div className="space-y-3 border-t border-dashed border-rule px-[18px] pb-4 pt-3">
              <div>
                <div className="font-mono text-[10px] uppercase tracking-wider text-ink-soft">Customer said</div>
                <div className="mt-1 whitespace-pre-wrap text-[13px] leading-normal text-ink">
                  {ticket.body || <span className="italic text-ink-soft">No message on file.</span>}
                </div>
              </div>
              <div>
                <div className="font-mono text-[10px] uppercase tracking-wider text-ink-soft">AI response</div>
                <div className="mt-1 whitespace-pre-wrap text-[13px] leading-normal text-ink">
                  {(ticket.final_reply as string) || (ticket.draft_reply as string) || (
                    <span className="italic text-ink-soft">No reply drafted yet.</span>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      {stampLabel && (
        <div
          key={`stamp-${flashKey}`}
          className={`postmark absolute right-4 top-3 flex h-[74px] w-[74px] animate-stampDown items-center justify-center rounded-full border-2 text-center font-mono text-[9.5px] font-bold uppercase leading-tight tracking-wide ${stampColor}`}
          style={{ transform: "rotate(-9deg)" }}
        >
          {stampLabel}
        </div>
      )}
    </div>
  );
}
