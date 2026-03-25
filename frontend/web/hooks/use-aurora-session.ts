"use client";

import { useEffect, useState } from "react";
import { ensureLocalSession, type AuroraSession } from "@/lib/local-session";

export function useAuroraSession() {
  const [session, setSession] = useState<AuroraSession | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function loadSession() {
      try {
        const currentSession = await ensureLocalSession();
        if (!cancelled) {
          setSession(currentSession);
          setError(null);
        }
      } catch (sessionError) {
        if (!cancelled) {
          setError(sessionError instanceof Error ? sessionError.message : "Failed to create local session");
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    void loadSession();

    return () => {
      cancelled = true;
    };
  }, []);

  return { session, loading, error };
}
