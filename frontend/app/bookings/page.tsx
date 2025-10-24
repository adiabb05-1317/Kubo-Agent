"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { Header } from "../_components/Header";
import { BackgroundOrbs } from "../_components/BackgroundOrbs";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { useAppStore } from "../store/useAppStore";
import { Calendar, Clock, DollarSign, Package } from "lucide-react";

export default function BookingsPage() {
  const router = useRouter();
  const user = useAppStore((state) => state.user);
  const logout = useAppStore((state) => state.logout);
  const fetchCurrentUser = useAppStore((state) => state.fetchCurrentUser);
  const bookings = useAppStore((state) => state.bookings);
  const isLoadingBookings = useAppStore((state) => state.isLoadingBookings);
  const loadMyBookings = useAppStore((state) => state.loadMyBookings);
  const pods = useAppStore((state) => state.pods);

  useEffect(() => {
    void fetchCurrentUser();
  }, [fetchCurrentUser]);

  useEffect(() => {
    if (user) {
      void loadMyBookings();
    }
  }, [user, loadMyBookings]);

  useEffect(() => {
    if (!user) {
      router.push("/auth");
    }
  }, [user, router]);

  if (!user) {
    return null;
  }

  const heroCopy = {
    title: "My Bookings",
    subtitle: "Track all your pod reservations in one place",
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleString("en-US", {
      month: "short",
      day: "numeric",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  const getPodName = (podId: number) => {
    const pod = pods.find((p) => p.id === podId);
    return pod?.name ?? `Pod #${podId}`;
  };

  const getStatusVariant = (status: string): "default" | "secondary" | "destructive" | "outline" => {
    switch (status) {
      case "confirmed":
        return "default";
      case "pending":
        return "secondary";
      case "cancelled":
        return "destructive";
      default:
        return "outline";
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "confirmed":
        return "bg-green-600/20 text-green-300 border-green-500/30";
      case "pending":
        return "bg-yellow-600/20 text-yellow-300 border-yellow-500/30";
      case "cancelled":
        return "bg-red-600/20 text-red-300 border-red-500/30";
      default:
        return "bg-slate-600/20 text-slate-300 border-slate-500/30";
    }
  };

  return (
    <div className="relative flex min-h-screen flex-col gap-10 px-6 pb-20 pt-10 md:px-12">
      <BackgroundOrbs />

      <Header heroCopy={heroCopy} isAuthenticated={true} onLogout={logout} />

      <main className="space-y-8">
        <div className="flex flex-col justify-between gap-4 md:flex-row md:items-center">
          <div>
            <h2 className="text-3xl font-bold text-white">Your Reservations</h2>
            <p className="mt-2 text-lg text-slate-300">
              View and manage all your pod bookings
            </p>
          </div>
          <div className="flex gap-3">
            <Button
              onClick={() => router.push("/")}
              variant="outline"
              className="border-white/20 text-white hover:bg-white/10"
            >
              <Package className="mr-2 h-4 w-4" />
              View Pods
            </Button>
            <Button
              onClick={() => void loadMyBookings()}
              variant="outline"
              className="border-white/20 text-white hover:bg-white/10"
            >
              Refresh
            </Button>
          </div>
        </div>

        {isLoadingBookings ? (
          <Card className="border-white/20 bg-slate-900/50">
            <CardContent className="py-12 text-center">
              <p className="text-lg text-slate-300">Loading bookings...</p>
            </CardContent>
          </Card>
        ) : bookings.length === 0 ? (
          <Card className="border-white/20 bg-slate-900/50">
            <CardContent className="py-12 text-center">
              <Package className="mx-auto mb-4 h-12 w-12 text-slate-400" />
              <p className="mb-4 text-lg text-slate-300">You haven't made any bookings yet.</p>
              <Button
                onClick={() => router.push("/")}
                className="bg-gradient-to-r from-blue-600 to-purple-600 text-white hover:from-blue-700 hover:to-purple-700"
              >
                Browse Pods
              </Button>
            </CardContent>
          </Card>
        ) : (
          <div className="grid gap-6 md:grid-cols-2 xl:grid-cols-3">
            {bookings.map((booking) => (
              <Card
                key={booking.id}
                className="border-white/20 bg-gradient-to-br from-slate-900/90 to-slate-800/90 transition-all hover:border-blue-500/50 hover:shadow-lg hover:shadow-blue-500/20"
              >
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <div>
                      <CardTitle className="text-xl text-white">{getPodName(booking.pod_id)}</CardTitle>
                      <CardDescription className="text-slate-400">
                        Booking #{booking.id}
                      </CardDescription>
                    </div>
                    <Badge
                      variant="outline"
                      className={`capitalize ${getStatusColor(booking.status)}`}
                    >
                      {booking.status}
                    </Badge>
                  </div>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-3">
                    <div className="flex items-start gap-3">
                      <Calendar className="mt-0.5 h-4 w-4 text-blue-400" />
                      <div>
                        <p className="text-xs text-slate-400">Start Time</p>
                        <p className="text-sm font-medium text-white">{formatDate(booking.start_time)}</p>
                      </div>
                    </div>
                    <div className="flex items-start gap-3">
                      <Clock className="mt-0.5 h-4 w-4 text-purple-400" />
                      <div>
                        <p className="text-xs text-slate-400">End Time</p>
                        <p className="text-sm font-medium text-white">{formatDate(booking.end_time)}</p>
                      </div>
                    </div>
                    <div className="flex items-start gap-3 rounded-lg border border-white/10 bg-slate-900/50 p-3">
                      <DollarSign className="mt-0.5 h-4 w-4 text-green-400" />
                      <div>
                        <p className="text-xs text-slate-400">Total Price</p>
                        <p className="text-lg font-semibold text-white">
                          {(booking.total_price_cents / 100).toLocaleString("en-US", {
                            style: "currency",
                            currency: "USD",
                          })}
                        </p>
                      </div>
                    </div>
                  </div>

                  <Button
                    onClick={() => router.push(`/pods/${booking.pod_id}`)}
                    variant="outline"
                    className="w-full border-white/20 text-white hover:bg-white/10"
                  >
                    View Pod Details
                  </Button>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
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
