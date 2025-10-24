"use client";

import { BookingDraft, Pod } from "../types";

interface PodsGridProps {
  isAuthenticated: boolean;
  pods: Pod[];
  drafts: Record<number, BookingDraft>;
  statusMessage: string | null;
  statusVariant: "success" | "error" | null;
  onDraftChange: (podId: number, draft: Partial<BookingDraft>) => void;
  onBookPod: (pod: Pod) => Promise<void> | void;
  onReload: () => Promise<void> | void;
}

export function PodsGrid({
  isAuthenticated,
  pods,
  drafts,
  statusMessage,
  statusVariant,
  onDraftChange,
  onBookPod,
  onReload,
}: PodsGridProps) {
  return (
    <section id="pods" className="glass-panel gradient-border flex flex-col gap-8 p-8">
      <div className="flex flex-col gap-2">
        <span className="text-sm uppercase tracking-[0.3em] text-[rgba(255,255,255,0.6)]">Pods</span>
        <div className="flex flex-col justify-between gap-3 md:flex-row md:items-center">
          <h2 className="text-2xl font-semibold">Reserve immersive workspace pods</h2>
          {isAuthenticated ? (
            <button
              onClick={() => void onReload()}
              className="rounded-full border border-[rgba(47,128,237,0.5)] px-4 py-2 text-xs uppercase tracking-widest text-[rgba(169,196,255,0.9)] transition hover:border-white"
            >
              Refresh pods
            </button>
          ) : null}
        </div>
        <p className="max-w-3xl text-sm text-[rgba(230,235,255,0.65)]">
          Browse pods curated for different moods and team sizes. Pick a time window to confirm your booking instantly.
        </p>
      </div>

      {!isAuthenticated ? (
        <div className="rounded-2xl border border-[rgba(255,255,255,0.1)] bg-[rgba(7,11,25,0.92)] px-6 py-5 text-sm text-[rgba(255,255,255,0.65)]">
          Log in to fetch pod availability and book your session.
        </div>
      ) : (
        <div className="grid gap-6 md:grid-cols-2 xl:grid-cols-3">
          {pods.map((pod) => (
            <article key={pod.id} className="glass-panel relative flex flex-col gap-5 rounded-3xl p-6 transition hover:card-highlight">
              <header className="flex items-start justify-between gap-3">
                <div>
                  <h3 className="text-xl font-semibold text-white">{pod.name}</h3>
                  <p className="text-xs uppercase tracking-[0.3em] text-[rgba(186,198,255,0.6)]">Capacity {pod.capacity}</p>
                </div>
                <span className="rounded-full bg-[rgba(47,128,237,0.18)] px-3 py-1 text-xs text-[rgba(181,204,255,0.9)]">
                  {(pod.price_cents / 100).toLocaleString("en-US", {
                    style: "currency",
                    currency: "USD",
                  })}
                </span>
              </header>
              <p className="min-h-[60px] text-sm text-[rgba(214,224,255,0.7)]">{pod.description ?? "No description"}</p>
              <div className="flex flex-col gap-3 text-xs text-[rgba(200,211,255,0.75)]">
                <label className="flex flex-col gap-2">
                  Start time
                  <input
                    type="datetime-local"
                    value={drafts[pod.id]?.start ?? getDefaultStart()}
                    onChange={(event) => onDraftChange(pod.id, { start: event.target.value })}
                    className="rounded-xl border border-transparent bg-[rgba(6,10,24,0.92)] px-3 py-2 text-[rgba(227,232,255,0.9)] outline-none focus:border-[rgba(47,128,237,0.5)]"
                  />
                </label>
                <label className="flex flex-col gap-2">
                  End time
                  <input
                    type="datetime-local"
                    value={drafts[pod.id]?.end ?? getDefaultEnd()}
                    onChange={(event) => onDraftChange(pod.id, { end: event.target.value })}
                    className="rounded-xl border border-transparent bg-[rgba(6,10,24,0.92)] px-3 py-2 text-[rgba(227,232,255,0.9)] outline-none focus:border-[rgba(47,128,237,0.5)]"
                  />
                </label>
              </div>
              <button
                className="mt-auto rounded-full border border-transparent bg-[rgba(47,128,237,0.85)] px-4 py-2 text-xs uppercase tracking-[0.2em] text-white transition hover:bg-[rgba(47,128,237,0.95)]"
                onClick={() => void onBookPod(pod)}
              >
                Book pod
              </button>
            </article>
          ))}
        </div>
      )}

      {statusMessage ? (
        <div
          className={`rounded-2xl px-6 py-4 text-sm ${
            statusVariant === "success"
              ? "border border-[rgba(72,255,203,0.35)] bg-[rgba(72,255,203,0.16)] text-[rgba(185,255,230,0.85)]"
              : "border border-[rgba(255,75,75,0.35)] bg-[rgba(255,75,75,0.18)] text-[rgba(255,165,165,0.9)]"
          }`}
        >
          {statusMessage}
        </div>
      ) : null}
    </section>
  );
}

function getDefaultStart() {
  return new Date(Date.now() + 30 * 60 * 1000).toISOString().slice(0, 16);
}

function getDefaultEnd() {
  return new Date(Date.now() + 90 * 60 * 1000).toISOString().slice(0, 16);
}


