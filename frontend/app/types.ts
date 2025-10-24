export type AuthMode = "login" | "signup";

export interface SessionUser {
  id: number;
  email: string;
}

export interface Pod {
  id: number;
  name: string;
  description: string | null;
  capacity: number;
  price_cents: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface BookingDraft {
  start: string;
  end: string;
}

export interface BookingPayload {
  user_id: number;
  pod_id: number;
  start_time: string;
  end_time: string;
  total_price_cents: number;
  status: "pending" | "confirmed" | "cancelled";
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
}

export interface HeroCopy {
  title: string;
  subtitle: string;
}

