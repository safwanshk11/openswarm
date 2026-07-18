import type { Ticket } from "../types";
import TicketCard from "./TicketCard";

interface SortingTrayProps {
  tickets: Ticket[];
  flashIds: Set<string>;
}

export default function SortingTray({ tickets, flashIds }: SortingTrayProps) {
  const done = tickets.filter((t) => t.status !== "unprocessed" && t.status !== "in_progress").length;

  return (
    <div className="p-7 px-8 stack:p-6">
      <div className="mb-4 flex items-baseline justify-between gap-3">
        <h2 className="m-0 font-serif text-[17px] font-semibold">Sorting tray</h2>
        <span className="font-mono text-[11px] tracking-wide text-ink-soft">
          {done} / {tickets.length} processed
        </span>
      </div>
      <div className="flex flex-col gap-3.5">
        {tickets.map((t) => (
          <TicketCard key={t.id} ticket={t} flash={flashIds.has(t.id)} />
        ))}
      </div>
    </div>
  );
}
