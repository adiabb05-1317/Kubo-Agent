"use client";

import { AuthMode } from "../types";

interface AuthCardProps {
  mode: AuthMode;
  email: string;
  password: string;
  isSubmitting: boolean;
  error: string | null;
  userEmail: string | null;
  onModeChange: (mode: AuthMode) => void;
  onEmailChange: (value: string) => void;
  onPasswordChange: (value: string) => void;
  onSubmit: () => Promise<void> | void;
}

export function AuthCard({
  mode,
  email,
  password,
  isSubmitting,
  error,
  userEmail,
  onModeChange,
  onEmailChange,
  onPasswordChange,
  onSubmit,
}: AuthCardProps) {
  return (
    <section id="auth" className="glass-panel gradient-border grid gap-8 p-8 md:grid-cols-[360px_auto]">
      <div className="flex flex-col gap-4">
        <span className="text-sm uppercase tracking-[0.3em] text-[rgba(255,255,255,0.65)]">Access</span>
        <h2 className="text-2xl font-semibold">{mode === "login" ? "Welcome back" : "Create your Kubo ID"}</h2>
        <p className="text-sm text-[rgba(255,255,255,0.65)]">
          {mode === "login"
            ? "Log in to manage bookings, receive concierge updates, and track sessions in real-time."
            : "Signup with just your email to reserve pods, invite guests, and sync your AI concierge."}
        </p>
        <div className="flex items-center gap-2 text-xs text-[rgba(255,255,255,0.5)]">
          <ModeButton active={mode === "login"} label="Login" onClick={() => onModeChange("login")} />
          <ModeButton active={mode === "signup"} label="Signup" onClick={() => onModeChange("signup")} />
        </div>
      </div>

      <div className="gradient-border relative flex flex-col gap-6 rounded-3xl p-8">
        <div className="flex flex-col gap-4">
          <Field label="Email" type="email" value={email} placeholder="you@company.com" onChange={onEmailChange} />
          <Field label="Password" type="password" value={password} placeholder="Enter password" onChange={onPasswordChange} />
        </div>

        {error ? (
          <div className="rounded-xl border border-[rgba(255,75,75,0.4)] bg-[rgba(255,75,75,0.18)] px-4 py-3 text-sm text-[rgba(255,125,125,0.9)]">
            {error}
          </div>
        ) : null}

        <button
          disabled={isSubmitting}
          onClick={() => void onSubmit()}
          className="group relative inline-flex items-center justify-center overflow-hidden rounded-full bg-[rgba(47,128,237,0.85)] px-6 py-3 text-sm font-semibold uppercase tracking-[0.2em] text-white transition hover:bg-[rgba(47,128,237,0.95)]"
        >
          <span className="absolute inset-0 bg-gradient-to-r from-[rgba(47,128,237,0.6)] to-[rgba(174,109,255,0.6)] opacity-0 transition group-hover:opacity-100" />
          <span className="relative">{isSubmitting ? "Processing..." : mode === "login" ? "Log in" : "Create account"}</span>
        </button>

        {userEmail ? <p className="text-xs text-[rgba(255,255,255,0.6)]">Signed in as {userEmail}</p> : null}
      </div>
    </section>
  );
}

function ModeButton({ active, label, onClick }: { active: boolean; label: string; onClick: () => void }) {
  return (
    <button
      className={`rounded-full px-4 py-2 font-medium transition ${active ? "bg-[rgba(47,128,237,0.25)] text-white" : "bg-transparent hover:bg-[rgba(255,255,255,0.08)]"}`}
      onClick={onClick}
    >
      {label}
    </button>
  );
}

function Field({
  label,
  type,
  value,
  placeholder,
  onChange,
}: {
  label: string;
  type: string;
  value: string;
  placeholder: string;
  onChange: (value: string) => void;
}) {
  return (
    <label className="flex flex-col text-sm text-[rgba(255,255,255,0.7)]">
      {label}
      <input
        type={type}
        value={value}
        onChange={(event) => onChange(event.target.value)}
        placeholder={placeholder}
        className="mt-2 rounded-xl border border-transparent bg-[rgba(6,10,24,0.92)] px-4 py-3 text-base text-white outline-none transition focus:border-[rgba(47,128,237,0.5)]"
      />
    </label>
  );
}
