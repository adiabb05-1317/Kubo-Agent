"use client";

import { useEffect } from "react";
import { Header } from "./components/Header";
import { AuthCard } from "./components/AuthCard";
import { PodsGrid } from "./components/PodsGrid";
import { ChatPanel } from "./components/ChatPanel";
import { BackgroundOrbs } from "./components/BackgroundOrbs";
import { useAppStore } from "./store/useAppStore";

export default function HomePage() {
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
  const logout = useAppStore((state) => state.logout);
  const fetchCurrentUser = useAppStore((state) => state.fetchCurrentUser);

  const pods = useAppStore((state) => state.pods);
  const drafts = useAppStore((state) => state.bookingDrafts);
  const statusMessage = useAppStore((state) => state.podsStatusMessage);
  const setDraft = useAppStore((state) => state.setBookingDraft);
  const bookPod = useAppStore((state) => state.bookPod);
  const reloadPods = useAppStore((state) => state.loadPods);

  const messages = useAppStore((state) => state.chatMessages);
  const input = useAppStore((state) => state.chatInput);
  const isSending = useAppStore((state) => state.isChatSending);
  const setChatInput = useAppStore((state) => state.setChatInput);
  const sendMessage = useAppStore((state) => state.sendChatMessage);

  useEffect(() => {
    void fetchCurrentUser();
  }, [fetchCurrentUser]);

  const heroCopy = {
    title: "Craft your flow inside Kubo pods",
    subtitle:
      "Reserve immersive workspaces, track bookings, and collaborate with an AI concierge built for real-time updates.",
  };

  return (
    <div className="relative flex min-h-screen flex-col gap-10 px-6 pb-20 pt-10 text-foreground md:px-12">
      <BackgroundOrbs />

      <Header heroCopy={heroCopy} isAuthenticated={Boolean(user)} onLogout={logout} />

      <main className="flex flex-col gap-14">
        <AuthCard
          mode={authMode}
          email={email}
          password={password}
          isSubmitting={isSubmitting}
          error={authError}
          userEmail={user?.email ?? null}
          onModeChange={setAuthMode}
          onEmailChange={setEmail}
          onPasswordChange={setPassword}
          onSubmit={authenticate}
        />

        <PodsGrid
          isAuthenticated={Boolean(user)}
          pods={pods}
          drafts={drafts}
          statusMessage={statusMessage}
          statusVariant={statusMessage?.toLowerCase().includes("booked") ? "success" : statusMessage ? "error" : null}
          onDraftChange={setDraft}
          onBookPod={bookPod}
          onReload={reloadPods}
        />

        <ChatPanel
          messages={messages}
          input={input}
          canSend={Boolean(input.trim()) && !isSending}
          isSending={isSending}
          onInputChange={setChatInput}
          onSend={sendMessage}
        />
      </main>

      <footer className="flex flex-col items-center gap-2 text-xs text-[rgba(184,198,255,0.6)]">
        <p>Built for realtime experiences — pods, people, and pricing in sync.</p>
        <p>
          Need help? Email <a className="underline" href="mailto:support@kubo.app">support@kubo.app</a>
        </p>
      </footer>
    </div>
  );
}
