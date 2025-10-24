"use client";

import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";

interface HeaderProps {
  heroCopy: {
    title: string;
    subtitle: string;
  };
  isAuthenticated: boolean;
  onLogout: () => Promise<void> | void;
}

export function Header({ heroCopy, isAuthenticated, onLogout }: HeaderProps) {
  return (
    <header className="rounded-2xl border border-white/20 bg-gradient-to-br from-slate-900/90 to-slate-800/90 p-8 backdrop-blur-xl">
      <div className="flex flex-col gap-6 md:flex-row md:items-center md:justify-between">
        <div className="flex flex-col gap-3">
          <Badge variant="outline" className="w-fit border-blue-500/30 bg-blue-500/10 text-blue-300">
            <span className="mr-2 inline-block h-2 w-2 animate-pulse rounded-full bg-blue-400" />
            Pods live sync enabled
          </Badge>
          <h1 className="text-balance text-3xl font-bold tracking-tight text-white md:text-5xl">
            {heroCopy.title}
          </h1>
          <p className="max-w-2xl text-lg text-slate-300">{heroCopy.subtitle}</p>
        </div>
        <nav className="flex flex-wrap items-center gap-3">
          <Link href="/">
            <Button variant="ghost" className="text-white hover:bg-white/10">
              Pods
            </Button>
          </Link>
          {isAuthenticated ? (
            <>
              <Link href="/bookings">
                <Button variant="ghost" className="text-white hover:bg-white/10">
                  My Bookings
                </Button>
              </Link>
              <Link href="/chat">
                <Button variant="ghost" className="text-white hover:bg-white/10">
                  Try AI Chat
                </Button>
              </Link>
              <Button
                variant="outline"
                className="border-white/20 text-white hover:bg-white/10"
                onClick={() => void onLogout()}
              >
                Log out
              </Button>
            </>
          ) : (
            <Link href="/auth">
              <Button className="bg-gradient-to-r from-blue-600 to-purple-600 text-white hover:from-blue-700 hover:to-purple-700">
                Sign In
              </Button>
            </Link>
          )}
        </nav>
      </div>
    </header>
  );
}


