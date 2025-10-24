"use client";

import { useCallback, useEffect, useMemo, useState } from "react";

import { ChatMessage } from "../types";
import { useApi } from "./useApi";

export function useChat() {
  const { fetcher, headers } = useApi();
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [isSending, setIsSending] = useState(false);

  const loadHistory = useCallback(async () => {
    try {
      const history = await fetcher<ChatMessage[]>("/chat/history", { method: "GET" });
      setMessages(history);
    } catch (err) {
      console.warn("Chat history not available", err);
    }
  }, [fetcher]);

  useEffect(() => {
    void loadHistory();
  }, [loadHistory]);

  const sendMessage = useCallback(async () => {
    const trimmed = input.trim();
    if (!trimmed) return;

    const outgoing: ChatMessage = {
      id: crypto.randomUUID(),
      role: "user",
      content: trimmed,
    };
    setMessages((prev) => [...prev, outgoing]);
    setInput("");
    setIsSending(true);

    try {
      const reply = await fetcher<{ id?: string; reply?: string }>("/chat/send", {
        method: "POST",
        headers,
        body: JSON.stringify({ message: trimmed }),
      });

      setMessages((prev) => [
        ...prev,
        {
          id: reply.id ?? crypto.randomUUID(),
          role: "assistant",
          content: reply.reply ?? "Got it!",
        },
      ]);
    } catch (err) {
      console.error(err);
      setMessages((prev) => [
        ...prev,
        {
          id: crypto.randomUUID(),
          role: "assistant",
          content: "We couldn’t reach the concierge. Try again shortly.",
        },
      ]);
    } finally {
      setIsSending(false);
    }
  }, [fetcher, headers, input]);

  const canSend = useMemo(() => Boolean(input.trim()) && !isSending, [input, isSending]);

  return {
    messages,
    input,
    isSending,
    setInput,
    sendMessage,
    reload: loadHistory,
    canSend,
  };
}


