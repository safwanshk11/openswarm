import type { Ticket } from "../types";

const dotBase =
  "flex h-5 w-5 items-center justify-center rounded-full border-[1.5px] border-rule bg-paper-card font-mono text-[9.5px] font-semibold text-ink-soft transition-all duration-200 ease-out";

export default function StepTracker({ ticket }: { ticket: Ticket }) {
  if (ticket.reply_needed === false) {
    if (ticket.status === "held_for_digest") {
      return (
        <div className="flex items-center gap-1">
          <span className={`${dotBase} border-slot-blue bg-slot-blue text-paper-card`}>T</span>
        </div>
      );
    }
    return (
      <div className="flex items-center gap-1">
        <span className={dotBase}>T</span>
      </div>
    );
  }

  const tDone = !!ticket.tag;
  const sDone = !!ticket.draft_reply;
  const rDone = ticket.status === "approved" || ticket.status === "needs_revision";

  return (
    <div className="flex items-center gap-1">
      <span className={`${dotBase} ${tDone ? "border-slot-blue bg-slot-blue text-paper-card" : ""}`}>T</span>
      <span className="h-px w-2.5 bg-rule" />
      <span className={`${dotBase} ${sDone ? "border-ochre bg-ochre text-paper-card" : ""}`}>S</span>
      <span className="h-px w-2.5 bg-rule" />
      <span className={`${dotBase} ${rDone ? "border-postal-green bg-postal-green text-paper-card" : ""}`}>R</span>
    </div>
  );
}
