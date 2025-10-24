"use client";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { AuthMode } from "../types";

interface AuthCardProps {
  mode: AuthMode;
  email: string;
  password: string;
  isSubmitting: boolean;
  error: string | null;
  userEmail: string | null;
  onModeChange: (mode: AuthMode) => void;
  onEmailChange: (value: string) => void;
  onPasswordChange: (value: string) => void;
  onSubmit: () => Promise<void> | void;
}

export function AuthCard({
  mode,
  email,
  password,
  isSubmitting,
  error,
  userEmail,
  onModeChange,
  onEmailChange,
  onPasswordChange,
  onSubmit,
}: AuthCardProps) {
  return (
    <section id="auth" className="mx-auto max-w-5xl">
      <Card className="border-white/20 bg-gradient-to-br from-slate-900/90 to-slate-800/90 backdrop-blur-xl">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="text-3xl font-bold text-white">
                {mode === "login" ? "Welcome back" : "Create your account"}
              </CardTitle>
              <CardDescription className="mt-2 text-base text-slate-300">
                {mode === "login"
                  ? "Log in to manage bookings and track sessions in real-time."
                  : "Sign up to reserve pods and sync your AI concierge."}
              </CardDescription>
            </div>
          </div>
          <div className="flex items-center gap-2 pt-4">
            <Button
              variant={mode === "login" ? "default" : "outline"}
              size="sm"
              onClick={() => onModeChange("login")}
              className={mode === "login" ? "bg-blue-600 hover:bg-blue-700" : "border-white/20 text-white hover:bg-white/10"}
            >
              Login
            </Button>
            <Button
              variant={mode === "signup" ? "default" : "outline"}
              size="sm"
              onClick={() => onModeChange("signup")}
              className={mode === "signup" ? "bg-blue-600 hover:bg-blue-700" : "border-white/20 text-white hover:bg-white/10"}
            >
              Sign Up
            </Button>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="email" className="text-sm font-medium text-slate-200">
              Email
            </Label>
            <Input
              id="email"
              type="email"
              value={email}
              onChange={(e) => onEmailChange(e.target.value)}
              placeholder="you@company.com"
              className="border-white/20 bg-slate-900/50 text-white placeholder:text-slate-400"
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="password" className="text-sm font-medium text-slate-200">
              Password
            </Label>
            <Input
              id="password"
              type="password"
              value={password}
              onChange={(e) => onPasswordChange(e.target.value)}
              placeholder="Enter password"
              className="border-white/20 bg-slate-900/50 text-white placeholder:text-slate-400"
            />
          </div>

          {error ? (
            <div className="rounded-lg border border-red-500/50 bg-red-500/10 px-4 py-3 text-sm text-red-200">
              {error}
            </div>
          ) : null}

          <Button
            disabled={isSubmitting}
            onClick={() => void onSubmit()}
            className="w-full bg-gradient-to-r from-blue-600 to-purple-600 text-white hover:from-blue-700 hover:to-purple-700"
            size="lg"
          >
            {isSubmitting ? "Processing..." : mode === "login" ? "Log in" : "Create account"}
          </Button>

          {userEmail ? (
            <p className="text-center text-sm text-slate-400">Signed in as {userEmail}</p>
          ) : null}
        </CardContent>
      </Card>
    </section>
  );
}


