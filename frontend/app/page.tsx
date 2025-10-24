"use client";

import { useEffect } from "react";
import { Header } from "./_components/Header";
import { PodsGridSimple } from "./_components/PodsGridSimple";
import { BackgroundOrbs } from "./_components/BackgroundOrbs";
import { useAppStore } from "./store/useAppStore";

export default function HomePage() {
  const user = useAppStore((state) => state.user);
  const logout = useAppStore((state) => state.logout);
  const fetchCurrentUser = useAppStore((state) => state.fetchCurrentUser);
  const pods = useAppStore((state) => state.pods);
  const reloadPods = useAppStore((state) => state.loadPods);

  useEffect(() => {
    void fetchCurrentUser();
  }, [fetchCurrentUser]);

  const heroCopy = {
    title: "Craft your flow inside Kubo pods",
    subtitle:
      "Reserve immersive workspaces, track bookings, and collaborate with an AI concierge built for real-time updates.",
  };

  return (
    <div className="relative flex min-h-screen flex-col gap-10 px-6 pb-20 pt-10 md:px-12">
      <BackgroundOrbs />

      <Header heroCopy={heroCopy} isAuthenticated={Boolean(user)} onLogout={logout} />

      <main className="flex flex-col gap-8">
        <PodsGridSimple
          isAuthenticated={Boolean(user)}
          pods={pods}
          onReload={reloadPods}
        />
      </main>

      <footer className="flex flex-col items-center gap-2 text-xs text-slate-400">
        <p>Built for realtime experiences — pods, people, and pricing in sync.</p>
        <p>
          Need help? Email <a className="text-blue-400 underline hover:text-blue-300" href="mailto:support@kubo.app">support@kubo.app</a>
        </p>
      </footer>
    </div>
  );
}
