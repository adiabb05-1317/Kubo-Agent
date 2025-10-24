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

export function PodsGrid({ isAuthenticated, pods, drafts, statusMessage, statusVariant, onDraftChange, onBookPod, onReload }: PodsGridProps) {
  return (
    <section id="pods" className="glass-panel gradient-border flex flex-col gap-6 p-8">
      <div className="flex items-center justify-between">
        <div className="flex flex-col gap-2">
          <span className="text-sm uppercase tracking-[0.3em] text-[rgba(255,255,255,0.65)]">Pods</span>
          <h2 className="text-2xl font-semibold">Browse available pods</h2>
        </div>
        <button onClick={() => void onReload()} className="rounded-full bg-[rgba(255,255,255,0.12)] px-4 py-2 text-xs font-semibold uppercase tracking-[0.18em] text-white transition hover:bg-[rgba(255,255,255,0.2)]">
          Refresh
        </button>
      </div>

      {statusMessage ? (
        <div className={`rounded-xl px-4 py-3 text-sm ${statusVariant === "success" ? "border border-[rgba(72,255,203,0.5)] bg-[rgba(72,255,203,0.12)] text-[rgba(189,255,231,0.95)]" : "border border-[rgba(255,75,75,0.4)] bg-[rgba(255,75,75,0.18)] text-[rgba(255,180,180,0.95)]"}`}>
          {statusMessage}
        </div>
      ) : null}

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {pods.map((pod) => {
          const draft = drafts[pod.id] ?? { start: "", end: "" };
          return (
            <div key={pod.id} className="gradient-border flex flex-col gap-4 rounded-3xl p-6">
              <div className="flex items-center justify-between">
                <div className="flex flex-col">
                  <span className="text-lg font-semibold text-white">{pod.name}</span>
                  <span className="text-xs text-[rgba(210,220,255,0.7)]">Capacity {pod.capacity} • ${(pod.price_cents / 100).toFixed(2)}</span>
                </div>
                <span className={`rounded-full px-3 py-1 text-xs ${pod.is_active ? "bg-[rgba(72,255,203,0.18)] text-[rgba(189,255,231,0.9)]" : "bg-[rgba(255,75,75,0.18)] text-[rgba(255,180,180,0.95)]"}`}>{pod.is_active ? "Active" : "Inactive"}</span>
              </div>

              {pod.description ? <p className="text-sm text-[rgba(210,220,255,0.8)]">{pod.description}</p> : null}

              <div className="grid grid-cols-2 gap-3">
                <label className="text-xs text-[rgba(220,230,255,0.8)]">
                  Start
                  <input
                    type="datetime-local"
                    value={draft.start}
                    onChange={(e) => onDraftChange(pod.id, { start: e.target.value })}
                    className="mt-1 w-full rounded-xl border border-transparent bg-[rgba(6,10,24,0.92)] px-3 py-2 text-sm text-white outline-none focus:border-[rgba(47,128,237,0.5)]"
                  />
                </label>
                <label className="text-xs text-[rgba(220,230,255,0.8)]">
                  End
                  <input
                    type="datetime-local"
                    value={draft.end}
                    onChange={(e) => onDraftChange(pod.id, { end: e.target.value })}
                    className="mt-1 w-full rounded-xl border border-transparent bg-[rgba(6,10,24,0.92)] px-3 py-2 text-sm text-white outline-none focus:border-[rgba(47,128,237,0.5)]"
                  />
                </label>
              </div>

              <button
                disabled={!isAuthenticated}
                onClick={() => void onBookPod(pod)}
                className="rounded-full bg-[rgba(47,128,237,0.85)] px-5 py-2 text-xs uppercase tracking-[0.2em] text-white transition hover:bg-[rgba(47,128,237,0.95)] disabled:cursor-not-allowed disabled:bg-[rgba(47,128,237,0.35)]"
              >
                {isAuthenticated ? "Book" : "Login to book"}
              </button>
            </div>
          );
        })}
      </div>
    </section>
  );
}
