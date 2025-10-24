"use client";

import { useCallback, useMemo } from "react";

const DEFAULT_BASE_URL = "http://127.0.0.1:8000";

export function useApi() {
  const baseUrl = useMemo(() => process.env.NEXT_PUBLIC_API_URL ?? DEFAULT_BASE_URL, []);

  const jsonHeaders = useMemo(
    () => ({
      "Content-Type": "application/json",
    }),
    []
  );

  const fetcher = useCallback(
    async <T>(path: string, init?: RequestInit): Promise<T> => {
      const response = await fetch(`${baseUrl}${path}`, {
        credentials: "include",
        ...init,
      });

      if (!response.ok) {
        const payload = await response.json().catch(() => ({}));
        throw new Error(payload.detail ?? payload.message ?? `Request failed: ${response.status}`);
      }

      return (await response.json()) as T;
    },
    [baseUrl]
  );

  return { baseUrl, headers: jsonHeaders, fetcher };
}


