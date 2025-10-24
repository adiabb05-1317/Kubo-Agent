"use client";

import { ChatMessage } from "../types";

interface ChatPanelProps {
  messages: ChatMessage[];
  input: string;
  canSend: boolean;
  isSending: boolean;
  onInputChange: (value: string) => void;
  onSend: () => Promise<void> | void;
}

export function ChatPanel({ messages, input, canSend, isSending, onInputChange, onSend }: ChatPanelProps) {
  return (
    <section id="chat" className="glass-panel gradient-border grid gap-8 p-8 md:grid-cols-[360px_auto]">
      <div className="flex flex-col gap-4">
        <span className="text-sm uppercase tracking-[0.3em] text-[rgba(255,255,255,0.6)]">AI Concierge</span>
        <h2 className="text-2xl font-semibold">Ask Kubo anything</h2>
        <p className="text-sm text-[rgba(230,235,255,0.7)]">
          Plan team offsites, adjust bookings, or troubleshoot in real-time. Kubo Agent keeps everything in sync with your pods and guests.
        </p>
      </div>

      <div className="gradient-border relative flex h-full flex-col gap-6 rounded-3xl p-6">
        <div className="flex flex-1 flex-col gap-4 overflow-auto rounded-2xl border border-[rgba(47,128,237,0.2)] bg-[rgba(5,7,17,0.8)] p-4 text-sm text-[rgba(222,228,255,0.85)]">
          {messages.length === 0 ? (
            <EmptyState />
          ) : (
            messages.map((message) => <ChatBubble key={message.id} message={message} />)
          )}
        </div>
        <div className="flex items-center gap-3 rounded-full border border-[rgba(47,128,237,0.4)] bg-[rgba(5,7,20,0.9)] px-3 py-2">
          <input
            value={input}
            onChange={(event) => onInputChange(event.target.value)}
            placeholder="Ask for scheduling help, add guests, or request pricing"
            className="flex-1 rounded-full border-none bg-transparent px-3 py-2 text-sm text-white outline-none placeholder:text-[rgba(180,198,255,0.6)]"
          />
          <button
            onClick={() => void onSend()}
            disabled={!canSend}
            className="rounded-full bg-[rgba(47,128,237,0.85)] px-4 py-2 text-xs uppercase tracking-[0.2em] text-white transition hover:bg-[rgba(47,128,237,0.95)] disabled:cursor-not-allowed disabled:bg-[rgba(47,128,237,0.35)]"
          >
            {isSending ? "Sending..." : "Send"}
          </button>
        </div>
      </div>
    </section>
  );
}

function EmptyState() {
  return (
    <div className="flex flex-col items-center justify-center gap-2 py-12 text-center text-[rgba(194,206,255,0.65)]">
      <span className="text-lg font-medium text-white">Start a conversation</span>
      <span className="text-xs tracking-wide uppercase">We keep the last thread for context</span>
    </div>
  );
}

function ChatBubble({ message }: { message: ChatMessage }) {
  const isAssistant = message.role === "assistant";
  return (
    <div
      className={`max-w-[85%] rounded-2xl px-4 py-3 text-sm leading-relaxed ${
        isAssistant
          ? "self-start bg-[rgba(47,128,237,0.18)] text-[rgba(227,235,255,0.9)]"
          : message.role === "tool"
            ? "self-start bg-[rgba(255,202,40,0.18)] text-[rgba(255,247,186,0.9)]"
            : "self-end bg-[rgba(72,255,203,0.22)] text-[rgba(212,255,239,0.9)]"
      }`}
    >
      {message.content}
    </div>
  );
}
