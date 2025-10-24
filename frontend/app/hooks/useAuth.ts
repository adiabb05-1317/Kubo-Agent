"use client";

import { useCallback, useEffect, useMemo, useState } from "react";

import { AuthMode, SessionUser } from "../types";
import { useApi } from "./useApi";

interface AuthState {
  mode: AuthMode;
  email: string;
  password: string;
  isSubmitting: boolean;
  error: string | null;
  user: SessionUser | null;
}

const initialState: AuthState = {
  mode: "login",
  email: "",
  password: "",
  isSubmitting: false,
  error: null,
  user: null,
};

export function useAuth() {
  const { fetcher, headers } = useApi();
  const [state, setState] = useState<AuthState>(initialState);

  useEffect(() => {
    fetcher<SessionUser>("/auth/me", { method: "GET" })
      .then((user) => {
        setState((prev) => ({ ...prev, user }));
      })
      .catch(() => {
        setState((prev) => ({ ...prev, user: null }));
      });
  }, [fetcher]);

  const setMode = useCallback((mode: AuthMode) => {
    setState((prev) => ({ ...prev, mode }));
  }, []);

  const setEmail = useCallback((value: string) => {
    setState((prev) => ({ ...prev, email: value }));
  }, []);

  const setPassword = useCallback((value: string) => {
    setState((prev) => ({ ...prev, password: value }));
  }, []);

  const resetCredentials = useCallback(() => {
    setState((prev) => ({ ...prev, email: "", password: "" }));
  }, []);

  const authenticate = useCallback(async () => {
    const { mode, email, password } = state;
    setState((prev) => ({ ...prev, isSubmitting: true, error: null }));

    try {
      const payload: Record<string, unknown> = { email, password };

      const user = await fetcher<SessionUser>(`/auth/${mode === "login" ? "login" : "register"}`, {
        method: "POST",
        headers,
        body: JSON.stringify(payload),
      });

      setState((prev) => ({ ...prev, user, isSubmitting: false, error: null }));
      resetCredentials();
      return user;
    } catch (err) {
      setState((prev) => ({
        ...prev,
        isSubmitting: false,
        error: err instanceof Error ? err.message : "Authentication failed",
      }));
      throw err;
    }
  }, [fetcher, headers, resetCredentials, state]);

  const logout = useCallback(async () => {
    try {
      await fetcher("/auth/logout", { method: "POST" });
    } finally {
      setState((prev) => ({ ...prev, user: null }));
    }
  }, [fetcher]);

  return useMemo(
    () => ({
      state,
      setMode,
      setEmail,
      setPassword,
      authenticate,
      logout,
    }),
    [authenticate, logout, setEmail, setMode, setPassword, state]
  );
}


