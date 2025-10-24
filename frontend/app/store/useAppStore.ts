"use client";

import { create } from "zustand";

import { AuthMode, BookingDraft, ChatMessage, Pod, SessionUser } from "../types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000";
const JSON_HEADERS = { "Content-Type": "application/json" } satisfies Record<string, string>;

async function apiFetch<T>(path: string, init: RequestInit = {}): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    credentials: "include",
    headers: { ...JSON_HEADERS, ...(init.headers ?? {}) },
    ...init,
  });

  if (!response.ok) {
    const payload = await response.json().catch(() => ({}));
    throw new Error(payload.detail ?? payload.message ?? `Request failed: ${response.status}`);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return (await response.json()) as T;
}

interface AppState {
  authMode: AuthMode;
  user: SessionUser | null;
  email: string;
  password: string;
  authError: string | null;
  isAuthSubmitting: boolean;

  pods: Pod[];
  bookingDrafts: Record<number, BookingDraft>;
  podsStatusMessage: string | null;

  chatMessages: ChatMessage[];
  chatInput: string;
  isChatSending: boolean;

  setAuthMode: (mode: AuthMode) => void;
  setEmail: (value: string) => void;
  setPassword: (value: string) => void;

  fetchCurrentUser: () => Promise<void>;
  authenticate: () => Promise<void>;
  logout: () => Promise<void>;

  loadPods: () => Promise<void>;
  setBookingDraft: (podId: number, draft: Partial<BookingDraft>) => void;
  bookPod: (pod: Pod) => Promise<void>;

  loadChatHistory: () => Promise<void>;
  setChatInput: (value: string) => void;
  sendChatMessage: () => Promise<void>;
}

const defaultDraft = (): BookingDraft => ({
  start: new Date(Date.now() + 30 * 60 * 1000).toISOString().slice(0, 16),
  end: new Date(Date.now() + 90 * 60 * 1000).toISOString().slice(0, 16),
});

export const useAppStore = create<AppState>((set, get) => ({
  authMode: "login",
  user: null,
  email: "",
  password: "",
  authError: null,
  isAuthSubmitting: false,

  pods: [],
  bookingDrafts: {},
  podsStatusMessage: null,

  chatMessages: [],
  chatInput: "",
  isChatSending: false,

  setAuthMode: (mode) => set({ authMode: mode }),
  setEmail: (value) => set({ email: value }),
  setPassword: (value) => set({ password: value }),

  fetchCurrentUser: async () => {
    try {
      const user = await apiFetch<SessionUser>("/auth/me", { method: "GET" });
      set({ user });
      await Promise.all([get().loadPods(), get().loadChatHistory()]);
    } catch {
      set({ user: null });
    }
  },

  authenticate: async () => {
    const { authMode, email, password } = get();
    set({ isAuthSubmitting: true, authError: null });

    try {
      const user = await apiFetch<SessionUser>(`/auth/${authMode === "login" ? "login" : "register"}`, {
        method: "POST",
        body: JSON.stringify({ email, password }),
      });
      set({ user, email: "", password: "", isAuthSubmitting: false, authError: null });
      await Promise.all([get().loadPods(), get().loadChatHistory()]);
    } catch (err) {
      set({
        isAuthSubmitting: false,
        authError: err instanceof Error ? err.message : "Authentication failed",
      });
      throw err;
    }
  },

  logout: async () => {
    try {
      await apiFetch("/auth/logout", { method: "POST" });
    } finally {
      set({ user: null, pods: [], bookingDrafts: {}, chatMessages: [] });
    }
  },

  loadPods: async () => {
    const { user } = get();
    if (!user) return;
    try {
      const pods = await apiFetch<Pod[]>("/kubo/pods", { method: "GET" });
      set({ pods, podsStatusMessage: null });
    } catch (err) {
      set({ podsStatusMessage: err instanceof Error ? err.message : "Unable to load pods" });
    }
  },

  setBookingDraft: (podId, draft) => {
    set((state) => ({
      bookingDrafts: {
        ...state.bookingDrafts,
        [podId]: {
          start: draft.start ?? state.bookingDrafts[podId]?.start ?? defaultDraft().start,
          end: draft.end ?? state.bookingDrafts[podId]?.end ?? defaultDraft().end,
        },
      },
    }));
  },

  bookPod: async (pod) => {
    const { user, bookingDrafts } = get();
    if (!user) {
      set({ podsStatusMessage: "Login required to book" });
      return;
    }

    const draft = bookingDrafts[pod.id] ?? defaultDraft();
    if (!draft.start || !draft.end) {
      set({ podsStatusMessage: "Please select a start and end time" });
      return;
    }

    try {
      set({ podsStatusMessage: "Booking pod..." });
      const payload = {
        user_id: user.id,
        pod_id: pod.id,
        start_time: draft.start,
        end_time: draft.end,
        total_price_cents: pod.price_cents,
        status: "confirmed",
      };

      await apiFetch("/kubo/bookings", {
        method: "POST",
        body: JSON.stringify(payload),
      });

      set({ podsStatusMessage: `Pod "${pod.name}" booked successfully!` });
      setTimeout(() => set({ podsStatusMessage: null }), 4000);
    } catch (err) {
      set({ podsStatusMessage: err instanceof Error ? err.message : "Booking failed" });
    }
  },

  loadChatHistory: async () => {
    const { user } = get();
    if (!user) return;
    try {
      const history = await apiFetch<ChatMessage[]>("/chat/history", { method: "GET" });
      set({ chatMessages: history });
    } catch (err) {
      console.warn("Chat history not available", err);
    }
  },

  setChatInput: (value) => set({ chatInput: value }),

  sendChatMessage: async () => {
    const { chatInput } = get();
    const trimmed = chatInput.trim();
    if (!trimmed) return;

    const outgoing: ChatMessage = {
      id: crypto.randomUUID(),
      role: "user",
      content: trimmed,
    };
    set((state) => ({ chatMessages: [...state.chatMessages, outgoing], chatInput: "", isChatSending: true }));

    try {
      const reply = await apiFetch<{ id?: string; reply?: string }>("/chat/send", {
        method: "POST",
        body: JSON.stringify({ message: trimmed }),
      });

      set((state) => ({
        chatMessages: [
          ...state.chatMessages,
          {
            id: reply.id ?? crypto.randomUUID(),
            role: "assistant",
            content: reply.reply ?? "Got it!",
          },
        ],
      }));
    } catch (err) {
      console.error(err);
      set((state) => ({
        chatMessages: [
          ...state.chatMessages,
          {
            id: crypto.randomUUID(),
            role: "assistant",
            content: "We couldn’t reach the concierge. Try again shortly.",
          },
        ],
      }));
    } finally {
      set({ isChatSending: false });
    }
  },
}));
