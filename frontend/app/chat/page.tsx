"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { Header } from "../_components/Header";
import { ChatPanel } from "../_components/ChatPanel";
import { BackgroundOrbs } from "../_components/BackgroundOrbs";
import { useAppStore } from "../store/useAppStore";

export default function ChatPage() {
  const router = useRouter();
  const user = useAppStore((state) => state.user);
  const logout = useAppStore((state) => state.logout);
  const fetchCurrentUser = useAppStore((state) => state.fetchCurrentUser);

  const messages = useAppStore((state) => state.chatMessages);
  const input = useAppStore((state) => state.chatInput);
  const isSending = useAppStore((state) => state.isChatSending);
  const setChatInput = useAppStore((state) => state.setChatInput);
  const sendMessage = useAppStore((state) => state.sendChatMessage);
  const clearMessages = useAppStore((state) => state.clearChatMessages);

  useEffect(() => {
    void fetchCurrentUser();
  }, [fetchCurrentUser]);

  useEffect(() => {
    if (!user) {
      router.push("/auth");
    }
  }, [user, router]);

  if (!user) {
    return null;
  }

  const heroCopy = {
    title: "AI Concierge",
    subtitle: "Get help with bookings, scheduling, and pod recommendations",
  };

  return (
    <div className="relative flex min-h-screen flex-col gap-10 px-6 pb-20 pt-10 md:px-12">
      <BackgroundOrbs />

      <Header heroCopy={heroCopy} isAuthenticated={true} onLogout={logout} />

      <main className="flex flex-col gap-8">
        <ChatPanel
          messages={messages}
          input={input}
          canSend={Boolean(input.trim()) && !isSending}
          isSending={isSending}
          onInputChange={setChatInput}
          onSend={sendMessage}
          onClear={clearMessages}
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

