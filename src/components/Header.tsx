interface HeaderProps {
  onProcessNext: () => void;
  onPlayVoicemail: () => void;
  processDisabled: boolean;
  processLabel: string;
  voicemailDisabled: boolean;
}

export default function Header({
  onProcessNext,
  onPlayVoicemail,
  processDisabled,
  processLabel,
  voicemailDisabled,
}: HeaderProps) {
  return (
    <header className="flex flex-wrap items-center justify-between gap-4 border-b-2 border-ink bg-paper px-8 py-5">
      <div className="flex items-center gap-3.5">
        <div className="logomark">
          <span className="font-mono text-[10px] font-semibold tracking-wide">AI</span>
        </div>
        <div>
          <h1 className="m-0 font-title text-[26px] font-semibold tracking-wide">Hermes</h1>
        </div>
      </div>
      <div className="flex gap-2.5">
        <button
          className="rounded border-[1.5px] border-ink bg-transparent px-[18px] py-2.5 font-sans text-[13px] font-semibold uppercase tracking-wide text-ink transition-transform duration-75 ease-out hover:-translate-y-px active:translate-y-0 disabled:cursor-not-allowed disabled:opacity-40 disabled:translate-y-0 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-slot-blue"
          onClick={onPlayVoicemail}
          disabled={voicemailDisabled}
        >
          Play voicemail
        </button>
        <button
          className="rounded border-[1.5px] border-ink bg-ink px-[18px] py-2.5 font-sans text-[13px] font-semibold uppercase tracking-wide text-paper transition-transform duration-75 ease-out hover:-translate-y-px active:translate-y-0 disabled:cursor-not-allowed disabled:opacity-40 disabled:translate-y-0 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-slot-blue"
          onClick={onProcessNext}
          disabled={processDisabled}
        >
          {processLabel}
        </button>
      </div>
    </header>
  );
}
