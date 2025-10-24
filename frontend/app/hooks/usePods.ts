"use client";

import { useCallback, useEffect, useMemo, useState } from "react";

import { BookingDraft, BookingPayload, Pod, SessionUser } from "../types";
import { useApi } from "./useApi";

interface UsePodsOptions {
  user: SessionUser | null;
}

interface PodsState {
  pods: Pod[];
  drafts: Record<number, BookingDraft>;
  statusMessage: string | null;
  error: string | null;
}

const defaultDraft = (): BookingDraft => ({
  start: new Date(Date.now() + 30 * 60 * 1000).toISOString().slice(0, 16),
  end: new Date(Date.now() + 90 * 60 * 1000).toISOString().slice(0, 16),
});

export function usePods({ user }: UsePodsOptions) {
  const { fetcher, headers } = useApi();
  const [state, setState] = useState<PodsState>({ pods: [], drafts: {}, statusMessage: null, error: null });

  const loadPods = useCallback(async () => {
    if (!user) return;
    try {
      const pods = await fetcher<Pod[]>("/kubo/pods", { method: "GET" });
      setState((prev) => ({ ...prev, pods, error: null }));
    } catch (err) {
      setState((prev) => ({
        ...prev,
        error: err instanceof Error ? err.message : "Unable to load pods",
      }));
    }
  }, [fetcher, user]);

  useEffect(() => {
    void loadPods();
  }, [loadPods]);

  const setDraft = useCallback((podId: number, draft: Partial<BookingDraft>) => {
    setState((prev) => ({
      ...prev,
      drafts: {
        ...prev.drafts,
        [podId]: {
          start: draft.start ?? prev.drafts[podId]?.start ?? defaultDraft().start,
          end: draft.end ?? prev.drafts[podId]?.end ?? defaultDraft().end,
        },
      },
    }));
  }, []);

  const bookPod = useCallback(
    async (pod: Pod) => {
      if (!user) {
        setState((prev) => ({ ...prev, statusMessage: "Login required to book" }));
        return;
      }

      const draft = state.drafts[pod.id] ?? defaultDraft();
      if (!draft.start || !draft.end) {
        setState((prev) => ({ ...prev, statusMessage: "Please select a start and end time" }));
        return;
      }

      try {
        setState((prev) => ({ ...prev, statusMessage: "Booking pod..." }));
        const payload: BookingPayload = {
          user_id: user.id,
          pod_id: pod.id,
          start_time: draft.start,
          end_time: draft.end,
          total_price_cents: pod.price_cents,
          status: "confirmed",
        };

        await fetcher("/kubo/bookings", {
          method: "POST",
          headers,
          body: JSON.stringify(payload),
        });

        setState((prev) => ({ ...prev, statusMessage: `Pod "${pod.name}" booked successfully!` }));
        setTimeout(() => {
          setState((prev) => ({ ...prev, statusMessage: null }));
        }, 4000);
      } catch (err) {
        setState((prev) => ({
          ...prev,
          statusMessage: err instanceof Error ? err.message : "Booking failed",
        }));
      }
    },
    [fetcher, headers, state.drafts, user]
  );

  const statusVariant = useMemo(() => {
    if (!state.statusMessage) return null;
    return state.statusMessage.toLowerCase().includes("success") || state.statusMessage.toLowerCase().includes("booked")
      ? "success"
      : "error";
  }, [state.statusMessage]);

  return {
    pods: state.pods,
    drafts: state.drafts,
    statusMessage: state.statusMessage,
    statusVariant,
    error: state.error,
    setDraft,
    bookPod,
    reload: loadPods,
  };
}


