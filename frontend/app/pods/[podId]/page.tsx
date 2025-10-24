"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { Header } from "../../_components/Header";
import { ChatPanel } from "../../_components/ChatPanel";
import { BackgroundOrbs } from "../../_components/BackgroundOrbs";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useAppStore } from "../../store/useAppStore";
import { Pod } from "../../types";
import { ArrowLeft, Users, DollarSign, Calendar, Clock } from "lucide-react";

export default function PodDetailsPage() {
  const params = useParams();
  const router = useRouter();
  const podId = Number(params.podId);

  const user = useAppStore((state) => state.user);
  const logout = useAppStore((state) => state.logout);
  const fetchCurrentUser = useAppStore((state) => state.fetchCurrentUser);
  const pods = useAppStore((state) => state.pods);
  const drafts = useAppStore((state) => state.bookingDrafts);
  const statusMessage = useAppStore((state) => state.podsStatusMessage);
  const setDraft = useAppStore((state) => state.setBookingDraft);
  const bookPod = useAppStore((state) => state.bookPod);

  const messages = useAppStore((state) => state.chatMessages);
  const input = useAppStore((state) => state.chatInput);
  const isSending = useAppStore((state) => state.isChatSending);
  const setChatInput = useAppStore((state) => state.setChatInput);
  const sendMessage = useAppStore((state) => state.sendChatMessage);

  const [pod, setPod] = useState<Pod | null>(null);

  useEffect(() => {
    void fetchCurrentUser();
  }, [fetchCurrentUser]);

  useEffect(() => {
    const foundPod = pods.find((p) => p.id === podId);
    if (foundPod) {
      setPod(foundPod);
    }
  }, [pods, podId]);

  useEffect(() => {
    if (!user) {
      router.push("/auth");
    }
  }, [user, router]);

  if (!user) {
    return null;
  }

  if (!pod) {
    return (
      <div className="relative flex min-h-screen flex-col gap-10 px-6 pb-20 pt-10 md:px-12">
        <BackgroundOrbs />
        <Header heroCopy={{ title: "Pod Not Found", subtitle: "" }} isAuthenticated={true} onLogout={logout} />
        <main className="flex flex-col items-center gap-6">
          <Card className="border-white/20 bg-slate-900/50">
            <CardContent className="py-12 text-center">
              <p className="text-lg text-slate-300">Pod not found</p>
              <Button onClick={() => router.push("/")} className="mt-4" variant="outline">
                Back to Pods
              </Button>
            </CardContent>
          </Card>
        </main>
      </div>
    );
  }

  const draft = drafts[podId] ?? {
    start: new Date(Date.now() + 30 * 60 * 1000).toISOString().slice(0, 16),
    end: new Date(Date.now() + 90 * 60 * 1000).toISOString().slice(0, 16),
  };

  const heroCopy = {
    title: pod.name,
    subtitle: pod.description ?? "Reserve this immersive workspace pod",
  };

  return (
    <div className="relative flex min-h-screen flex-col gap-10 px-6 pb-20 pt-10 md:px-12">
      <BackgroundOrbs />

      <Header heroCopy={heroCopy} isAuthenticated={true} onLogout={logout} />

      <main className="flex flex-col gap-8">
        {/* Back Button */}
        <Button
          variant="ghost"
          onClick={() => router.push("/")}
          className="w-fit text-white hover:bg-white/10"
        >
          <ArrowLeft className="mr-2 h-4 w-4" />
          Back to all pods
        </Button>

        {/* Pod Details and Booking */}
        <div className="grid gap-8 lg:grid-cols-2">
          {/* Pod Information */}
          <Card className="border-white/20 bg-gradient-to-br from-slate-900/90 to-slate-800/90">
            <CardHeader>
              <div className="flex items-start justify-between">
                <CardTitle className="text-3xl text-white">{pod.name}</CardTitle>
                <Badge variant="secondary" className="bg-blue-600/20 text-blue-300 text-lg px-3 py-1">
                  {(pod.price_cents / 100).toLocaleString("en-US", {
                    style: "currency",
                    currency: "USD",
                  })}
                </Badge>
              </div>
              <CardDescription className="text-base text-slate-300">
                {pod.description ?? "No description available"}
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="grid gap-4 sm:grid-cols-2">
                <div className="flex items-center gap-3 rounded-lg border border-white/10 bg-slate-900/50 p-4">
                  <Users className="h-5 w-5 text-blue-400" />
                  <div>
                    <p className="text-sm text-slate-400">Capacity</p>
                    <p className="text-lg font-semibold text-white">{pod.capacity} people</p>
                  </div>
                </div>
                <div className="flex items-center gap-3 rounded-lg border border-white/10 bg-slate-900/50 p-4">
                  <DollarSign className="h-5 w-5 text-green-400" />
                  <div>
                    <p className="text-sm text-slate-400">Price per session</p>
                    <p className="text-lg font-semibold text-white">${(pod.price_cents / 100).toFixed(2)}</p>
                  </div>
                </div>
              </div>
              <div className="rounded-lg border border-white/10 bg-slate-900/50 p-4">
                <div className="flex items-center gap-2">
                  <div className={`h-3 w-3 rounded-full ${pod.is_active ? 'bg-green-400' : 'bg-red-400'}`} />
                  <p className="text-white">
                    Status: <span className="font-semibold">{pod.is_active ? "Available" : "Unavailable"}</span>
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Booking Form */}
          <Card className="border-white/20 bg-gradient-to-br from-slate-900/90 to-slate-800/90">
            <CardHeader>
              <CardTitle className="text-2xl text-white">Book This Pod</CardTitle>
              <CardDescription className="text-slate-300">
                Select your preferred time slot
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-2">
                <Label htmlFor="start-time" className="flex items-center gap-2 text-slate-200">
                  <Calendar className="h-4 w-4" />
                  Start time
                </Label>
                <Input
                  id="start-time"
                  type="datetime-local"
                  value={draft.start}
                  onChange={(e) => setDraft(podId, { start: e.target.value })}
                  className="border-white/20 bg-slate-900/50 text-white"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="end-time" className="flex items-center gap-2 text-slate-200">
                  <Clock className="h-4 w-4" />
                  End time
                </Label>
                <Input
                  id="end-time"
                  type="datetime-local"
                  value={draft.end}
                  onChange={(e) => setDraft(podId, { end: e.target.value })}
                  className="border-white/20 bg-slate-900/50 text-white"
                />
              </div>

              <Button
                onClick={() => void bookPod(pod)}
                className="w-full bg-gradient-to-r from-blue-600 to-purple-600 text-white hover:from-blue-700 hover:to-purple-700"
                size="lg"
              >
                Confirm Booking
              </Button>

              {statusMessage ? (
                <div
                  className={`rounded-lg px-4 py-3 text-sm ${
                    statusMessage.toLowerCase().includes("booked")
                      ? "border border-green-500/50 bg-green-500/10 text-green-200"
                      : "border border-red-500/50 bg-red-500/10 text-red-200"
                  }`}
                >
                  {statusMessage}
                </div>
              ) : null}
            </CardContent>
          </Card>
        </div>

        {/* AI Concierge Chat */}
        <ChatPanel
          messages={messages}
          input={input}
          canSend={Boolean(input.trim()) && !isSending}
          isSending={isSending}
          onInputChange={setChatInput}
          onSend={sendMessage}
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
