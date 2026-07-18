import { useEffect, useRef } from "react";
import type { TraceLine } from "../types";

interface TraceOverlayProps {
  open: boolean;
  lines: TraceLine[];
  onClose: () => void;
}

const AGENT_COLOR: Record<string, string> = {
  triage: "text-slot-blue",
  specialist: "text-ochre",
  reviewer: "text-postal-green",
  digest: "text-kraft",
  system: "text-ink-soft",
};

export default function TraceOverlay({ open, lines, onClose }: TraceOverlayProps) {
  const logRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (open && logRef.current) {
      logRef.current.scrollTop = logRef.current.scrollHeight;
    }
  }, [open, lines]);

  useEffect(() => {
    function onKeyDown(e: KeyboardEvent) {
      if (e.key === "Escape" && open) onClose();
    }
    document.addEventListener("keydown", onKeyDown);
    return () => document.removeEventListener("keydown", onKeyDown);
  }, [open, onClose]);

  if (!open) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-ink/35 p-10"
      onClick={(e) => {
        if (e.target === e.currentTarget) onClose();
      }}
    >
      <div
        role="dialog"
        aria-modal="true"
        aria-labelledby="traceModalTitle"
        className="flex max-h-full w-full max-w-[640px] flex-col rounded-md border-[1.5px] border-ink bg-paper-card shadow-modal"
      >
        <div className="flex items-center justify-between border-b-[1.5px] border-ink px-[18px] py-3.5">
          <h3 id="traceModalTitle" className="m-0 font-serif text-base font-semibold">
            Agent trace
          </h3>
          <button
            aria-label="Close agent trace"
            className="cursor-pointer border-none bg-transparent px-1.5 py-1 font-mono text-[13px] normal-case tracking-normal text-ink-soft hover:text-ink"
            onClick={onClose}
          >
            Close &times;
          </button>
        </div>
        <div
          ref={logRef}
          className="trace-log min-h-[200px] max-h-[60vh] flex-1 overflow-y-auto rounded-b-md px-[18px] py-1 font-mono text-[11.5px] leading-[1.7]"
        >
          {lines.map((line) => (
            <div key={line.id} className={`whitespace-pre-wrap break-words py-[3px] ${AGENT_COLOR[line.agent]}`}>
              <span className="mr-1.5 text-ink-soft">{line.time}</span>
              <span className="mr-1 font-bold">[{line.agent}]</span>
              {line.text}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
