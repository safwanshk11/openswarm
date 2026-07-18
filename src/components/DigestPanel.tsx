import type { Digest } from "../types";

interface DigestPanelProps {
  digest: Digest | null;
  onOpenTrace: () => void;
}

export default function DigestPanel({ digest, onOpenTrace }: DigestPanelProps) {
  return (
    <div className="flex min-h-[calc(100vh-89px)] flex-col border-l-2 border-ink p-7 px-6 stack:min-h-0 stack:border-l-0 stack:border-t-2">
      <div className="mb-4 flex items-baseline justify-between gap-3">
        <h2 className="m-0 font-serif text-[17px] font-semibold">Daily digest</h2>
        <button
          className="cursor-pointer border-none bg-transparent p-0 font-mono text-[11px] font-semibold tracking-wide text-slot-blue underline decoration-dotted underline-offset-[3px] hover:text-ink"
          onClick={onOpenTrace}
        >
          <span className="mr-1.5 inline-block h-1.5 w-1.5 rounded-full bg-slot-blue align-middle" />
          View agent trace
        </button>
      </div>

      <div className="digest-panel relative flex-1 overflow-y-auto rounded border border-digest-border bg-paper-shade p-[18px] pb-4">
        {!digest || !digest.ticket_count ? (
          <p className="m-0 text-[13px] italic text-ink-soft">Nothing held for digest yet.</p>
        ) : (
          <>
            <span className="font-mono text-[10.5px] tracking-wide text-kraft">
              {digest.ticket_count} ticket{digest.ticket_count === 1 ? "" : "s"} held
            </span>
            <p className="my-3 text-[13.5px] leading-relaxed">{digest.summary || ""}</p>
            <ul className="m-0 list-disc pl-[18px] text-[12.5px] text-ink-soft">
              {(digest.highlights || []).map((h, i) => (
                <li key={i} className="mb-1.5 leading-snug">
                  {h}
                </li>
              ))}
            </ul>
          </>
        )}
      </div>
    </div>
  );
}
