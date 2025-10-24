"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { AuthCard } from "../_components/AuthCard";
import { BackgroundOrbs } from "../_components/BackgroundOrbs";
import { useAppStore } from "../store/useAppStore";

export default function AuthPage() {
  const router = useRouter();
  const authMode = useAppStore((state) => state.authMode);
  const email = useAppStore((state) => state.email);
  const password = useAppStore((state) => state.password);
  const isSubmitting = useAppStore((state) => state.isAuthSubmitting);
  const authError = useAppStore((state) => state.authError);
  const user = useAppStore((state) => state.user);

  const setAuthMode = useAppStore((state) => state.setAuthMode);
  const setEmail = useAppStore((state) => state.setEmail);
  const setPassword = useAppStore((state) => state.setPassword);
  const authenticate = useAppStore((state) => state.authenticate);

  useEffect(() => {
    if (user) {
      router.push("/");
    }
  }, [user, router]);

  return (
    <div className="relative flex min-h-screen flex-col items-center justify-center gap-10 px-6 pb-20 pt-10">
      <BackgroundOrbs />

      <div className="z-10 w-full max-w-2xl space-y-8">
        <div className="text-center">
          <h1 className="text-5xl font-bold tracking-tight text-white">Kubo Pods</h1>
          <p className="mt-3 text-xl text-slate-300">
            Sign in to reserve your workspace
          </p>
        </div>

        <AuthCard
          mode={authMode}
          email={email}
          password={password}
          isSubmitting={isSubmitting}
          error={authError}
          userEmail={null}
          onModeChange={setAuthMode}
          onEmailChange={setEmail}
          onPasswordChange={setPassword}
          onSubmit={authenticate}
        />
      </div>

      <footer className="absolute bottom-6 flex flex-col items-center gap-2 text-xs text-slate-400">
        <p>Built for realtime experiences — pods, people, and pricing in sync.</p>
      </footer>
    </div>
  );
}

