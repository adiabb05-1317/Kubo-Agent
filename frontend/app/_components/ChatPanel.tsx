"use client";

import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { ChatMessage } from "../types";
import { Bot, User, Send, MessageSquare } from "lucide-react";

interface ChatPanelProps {
  messages: ChatMessage[];
  input: string;
  canSend: boolean;
  isSending: boolean;
  onInputChange: (value: string) => void;
  onSend: () => Promise<void> | void;
  onClear: () => void;
}

export function ChatPanel({ messages, input, canSend, isSending, onInputChange, onSend, onClear }: ChatPanelProps) {
  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" && canSend) {
      void onSend();
    }
  };

  return (
    <section id="chat" className="space-y-6">
      <div>
        <h2 className="text-3xl font-bold text-white">AI Concierge</h2>
        <p className="mt-2 text-lg text-slate-300">
          Ask Kubo anything about bookings, scheduling, or pod availability.
        </p>
      </div>

      <Card className="border-white/20 bg-gradient-to-br from-slate-900/90 to-slate-800/90">
        <CardHeader>
          <div className="flex items-start justify-between">
            <div>
              <CardTitle className="flex items-center gap-2 text-xl text-white">
                <MessageSquare className="h-5 w-5 text-blue-400" />
                Chat with Kubo Agent
              </CardTitle>
              <CardDescription className="text-slate-300">
                Get help with scheduling, bookings, or any questions about your workspace pods.
              </CardDescription>
            </div>
            {messages.length > 0 && (
              <Button
                variant="outline"
                size="sm"
                onClick={onClear}
                className="border-white/20 text-white hover:bg-white/10"
              >
                Clear Chat
              </Button>
            )}
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Chat Messages */}
          <div className="flex h-[400px] flex-col gap-4 overflow-y-auto rounded-lg border border-white/10 bg-slate-950/50 p-4">
            {messages.length === 0 ? (
              <EmptyState />
            ) : (
              messages.map((message) => <ChatBubble key={message.id} message={message} />)
            )}
          </div>

          {/* Input Area */}
          <div className="flex items-center gap-3">
            <Input
              value={input}
              onChange={(e) => onInputChange(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask for scheduling help, add guests, or request pricing..."
              className="border-white/20 bg-slate-900/50 text-white placeholder:text-slate-400"
            />
            <Button
              onClick={() => void onSend()}
              disabled={!canSend}
              className="bg-gradient-to-r from-blue-600 to-purple-600 text-white hover:from-blue-700 hover:to-purple-700 disabled:opacity-50"
            >
              {isSending ? (
                "Sending..."
              ) : (
                <>
                  <Send className="h-4 w-4" />
                </>
              )}
            </Button>
          </div>
        </CardContent>
      </Card>
    </section>
  );
}

function EmptyState() {
  return (
    <div className="flex h-full flex-col items-center justify-center gap-3 text-center">
      <Bot className="h-12 w-12 text-blue-400" />
      <div>
        <p className="text-lg font-semibold text-white">Start a conversation</p>
        <p className="text-sm text-slate-400">Ask me anything about pods, bookings, or scheduling</p>
      </div>
    </div>
  );
}

function ChatBubble({ message }: { message: ChatMessage }) {
  const isAssistant = message.role === "assistant";
  return (
    <div className={`flex items-start gap-3 ${isAssistant ? "" : "flex-row-reverse"}`}>
      <div
        className={`flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-full ${
          isAssistant ? "bg-blue-600/20" : "bg-purple-600/20"
        }`}
      >
        {isAssistant ? (
          <Bot className="h-4 w-4 text-blue-400" />
        ) : (
          <User className="h-4 w-4 text-purple-400" />
        )}
      </div>
      <div
        className={`max-w-[80%] rounded-lg px-4 py-2.5 ${
          isAssistant
            ? "bg-slate-800/80 text-slate-100"
            : "bg-gradient-to-r from-blue-600/20 to-purple-600/20 text-white"
        }`}
      >
        {isAssistant ? (
          <div className="prose prose-invert prose-sm max-w-none">
            <ReactMarkdown
              remarkPlugins={[remarkGfm]}
              components={{
                // Customize heading styles
                h1: ({ node, ...props }) => <h1 className="text-lg font-bold text-white mb-2" {...props} />,
                h2: ({ node, ...props }) => <h2 className="text-base font-semibold text-white mb-2" {...props} />,
                h3: ({ node, ...props }) => <h3 className="text-sm font-semibold text-white mb-1" {...props} />,
                // Customize paragraph styles
                p: ({ node, ...props }) => <p className="text-sm leading-relaxed text-slate-100 mb-2 last:mb-0" {...props} />,
                // Customize list styles
                ul: ({ node, ...props }) => <ul className="list-disc list-inside text-sm text-slate-100 mb-2 space-y-1" {...props} />,
                ol: ({ node, ...props }) => <ol className="list-decimal list-inside text-sm text-slate-100 mb-2 space-y-1" {...props} />,
                li: ({ node, ...props }) => <li className="text-sm text-slate-100" {...props} />,
                // Customize table styles
                table: ({ node, ...props }) => (
                  <div className="overflow-x-auto my-3">
                    <table className="min-w-full border-collapse border border-slate-600/50 text-sm" {...props} />
                  </div>
                ),
                thead: ({ node, ...props }) => <thead className="bg-slate-700/50" {...props} />,
                tbody: ({ node, ...props }) => <tbody className="divide-y divide-slate-600/30" {...props} />,
                tr: ({ node, ...props }) => <tr className="hover:bg-slate-700/30 transition-colors" {...props} />,
                th: ({ node, ...props }) => (
                  <th className="border border-slate-600/50 px-3 py-2 text-left font-semibold text-white" {...props} />
                ),
                td: ({ node, ...props }) => (
                  <td className="border border-slate-600/50 px-3 py-2 text-slate-100" {...props} />
                ),
                // Customize code styles
                code: ({ node, inline, ...props }: any) =>
                  inline ? (
                    <code className="rounded bg-slate-900/60 px-1.5 py-0.5 text-xs text-blue-300" {...props} />
                  ) : (
                    <code className="block rounded bg-slate-900/60 p-2 text-xs text-blue-300 overflow-x-auto" {...props} />
                  ),
                pre: ({ node, ...props }) => <pre className="rounded bg-slate-900/60 p-3 overflow-x-auto mb-2" {...props} />,
                // Customize link styles
                a: ({ node, ...props }) => <a className="text-blue-400 underline hover:text-blue-300" {...props} />,
                // Customize blockquote styles
                blockquote: ({ node, ...props }) => (
                  <blockquote className="border-l-4 border-blue-500/50 pl-3 italic text-slate-300 my-2" {...props} />
                ),
                // Customize strong/bold styles
                strong: ({ node, ...props }) => <strong className="font-semibold text-white" {...props} />,
                // Customize em/italic styles
                em: ({ node, ...props }) => <em className="italic text-slate-200" {...props} />,
                // Customize horizontal rule
                hr: ({ node, ...props }) => <hr className="border-slate-600/50 my-3" {...props} />,
              }}
            >
              {message.content}
            </ReactMarkdown>
          </div>
        ) : (
          <p className="text-sm leading-relaxed">{message.content}</p>
        )}
      </div>
    </div>
  );
}


