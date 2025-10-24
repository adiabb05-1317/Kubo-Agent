"use client";

import Link from "next/link";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Pod } from "../types";
import { Users, ArrowRight } from "lucide-react";

interface PodsGridSimpleProps {
  isAuthenticated: boolean;
  pods: Pod[];
  onReload: () => Promise<void> | void;
}

export function PodsGridSimple({ isAuthenticated, pods, onReload }: PodsGridSimpleProps) {
  return (
    <section id="pods" className="space-y-6">
      <div className="flex flex-col gap-4">
        <div className="flex flex-col justify-between gap-3 md:flex-row md:items-center">
          <div>
            <h2 className="text-3xl font-bold text-white">Workspace Pods</h2>
            <p className="mt-2 text-lg text-slate-300">
              Browse pods curated for different moods and team sizes. Click on a pod to view details and book.
            </p>
          </div>
          {isAuthenticated ? (
            <Button
              onClick={() => void onReload()}
              variant="outline"
              className="border-white/20 text-white hover:bg-white/10"
            >
              Refresh Pods
            </Button>
          ) : null}
        </div>
      </div>

      {!isAuthenticated ? (
        <Card className="border-white/20 bg-slate-900/50">
          <CardContent className="py-8 text-center">
            <p className="text-lg text-slate-300">
              Please <Link href="/auth" className="text-blue-400 underline hover:text-blue-300">sign in</Link> to view and book pods.
            </p>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-6 md:grid-cols-2 xl:grid-cols-3">
          {pods.map((pod) => (
            <Link key={pod.id} href={`/pods/${pod.id}`}>
              <Card className="group h-full border-white/20 bg-gradient-to-br from-slate-900/90 to-slate-800/90 transition-all hover:border-blue-500/50 hover:shadow-lg hover:shadow-blue-500/20">
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <CardTitle className="text-xl text-white">{pod.name}</CardTitle>
                    <Badge variant="secondary" className="bg-blue-600/20 text-blue-300">
                      {(pod.price_cents / 100).toLocaleString("en-US", {
                        style: "currency",
                        currency: "USD",
                      })}
                    </Badge>
                  </div>
                  <CardDescription className="flex items-center gap-2 text-slate-400">
                    <Users className="h-4 w-4" />
                    Capacity: {pod.capacity} people
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <p className="min-h-[60px] text-sm text-slate-300">
                    {pod.description ?? "No description available"}
                  </p>
                  <div className="flex items-center justify-between pt-2">
                    <span className="text-sm text-slate-400">
                      {pod.is_active ? "Available" : "Unavailable"}
                    </span>
                    <ArrowRight className="h-5 w-5 text-blue-400 transition-transform group-hover:translate-x-1" />
                  </div>
                </CardContent>
              </Card>
            </Link>
          ))}
        </div>
      )}
    </section>
  );
}

