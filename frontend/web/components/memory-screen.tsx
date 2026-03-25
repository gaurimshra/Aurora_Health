"use client";

import { useEffect, useState } from "react";
import { DashboardShell } from "@/components/dashboard-shell";
import { GlassCard } from "@/components/ui/glass-card";
import { GradientButton } from "@/components/ui/gradient-button";
import { useAuroraSession } from "@/hooks/use-aurora-session";
import { backendRequest } from "@/lib/backend";
import type { HistoryResponse, WeeklyReport } from "@/lib/api-types";

type MemorySearchResult = {
  query: string;
  results: Array<{
    memory_type: string;
    content: string;
    score: number;
    created_at: string;
  }>;
};

export function MemoryScreen() {
  const { session, loading: sessionLoading, error: sessionError } = useAuroraSession();
  const [history, setHistory] = useState<HistoryResponse | null>(null);
  const [report, setReport] = useState<WeeklyReport | null>(null);
  const [search, setSearch] = useState<MemorySearchResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [searching, setSearching] = useState(false);

  useEffect(() => {
    if (!session) return;
    const currentSession = session;

    Promise.all([
      backendRequest<HistoryResponse>("/tracking/history", currentSession.token),
      backendRequest<WeeklyReport>("/tracking/weekly-report", currentSession.token),
    ])
      .then(([historyResponse, reportResponse]) => {
        setHistory(historyResponse);
        setReport(reportResponse);
      })
      .catch((loadError) => setError(loadError instanceof Error ? loadError.message : "Failed to load memory data"));
  }, [session]);

  async function searchMemory(formData: FormData) {
    if (!session) return;
    try {
      setSearching(true);
      setError(null);
      const response = await backendRequest<MemorySearchResult>("/tracking/memory-search", session.token, {
        method: "POST",
        body: JSON.stringify({
          query: String(formData.get("query") ?? ""),
          top_k: Number(formData.get("top_k") ?? 5),
        }),
      });
      setSearch(response);
    } catch (searchError) {
      setError(searchError instanceof Error ? searchError.message : "Failed to search memory");
    } finally {
      setSearching(false);
    }
  }

  return (
    <DashboardShell
      eyebrow="Memory"
      title="History and memory retrieval"
      description={sessionLoading ? "Creating your local Aurora session..." : "This page surfaces raw tracking history, semantic memories, weekly reporting, and explicit memory search over the backend store."}
      headerStats={[
        { label: "Workouts", value: `${history?.workout_logs.length ?? 0}` },
        { label: "Progress", value: `${history?.progress_logs.length ?? 0}` },
        { label: "Memories", value: `${history?.recent_memories.length ?? 0}` },
      ]}
    >
      {sessionError ? <GlassCard><p className="text-white/70">{sessionError}</p></GlassCard> : null}
      {error ? <GlassCard><p className="text-white/70">{error}</p></GlassCard> : null}

      <div className="grid gap-6 xl:grid-cols-[0.9fr,1.1fr]">
        <GlassCard>
          <p className="section-label">Memory search</p>
          <h2 className="mt-3 text-2xl font-semibold">Query Aurora memory</h2>
          <form action={searchMemory} className="mt-5 space-y-4">
            <input className="input-shell" name="query" placeholder="low energy, protein consistency, strength days" />
            <input className="input-shell" name="top_k" type="number" min="1" max="20" defaultValue="5" />
            <GradientButton className="w-full" type="submit" disabled={!session || searching}>
              {searching ? "Searching..." : "Search Memory"}
            </GradientButton>
          </form>

          <div className="mt-6 grid gap-3">
            {(search?.results ?? []).map((item) => (
              <div key={`${item.created_at}-${item.content}`} className="rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white/70">
                <span className="mb-2 block text-xs uppercase tracking-[0.2em] text-cyan-200/70">{item.memory_type} · score {item.score.toFixed(2)}</span>
                {item.content}
              </div>
            ))}
            {search && search.results.length === 0 ? <div className="rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white/70">No memory matches found yet.</div> : null}
          </div>
        </GlassCard>

        <GlassCard>
          <p className="section-label">Weekly report</p>
          <h2 className="mt-3 text-2xl font-semibold">Operational summary</h2>
          <p className="mt-4 text-white/70">{report?.summary ?? "No weekly report available yet."}</p>
          <div className="mt-6 grid gap-3">
            {(report?.recommendations ?? []).map((item) => (
              <div key={item} className="rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white/70">
                {item}
              </div>
            ))}
          </div>
        </GlassCard>
      </div>

      <div className="grid gap-6 xl:grid-cols-2">
        <GlassCard>
          <p className="section-label">Recent semantic memories</p>
          <div className="mt-4 grid gap-3">
            {(history?.recent_memories ?? []).slice(0, 8).map((item, index) => (
              <div key={`${index}-${String(item.created_at ?? index)}`} className="rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white/70">
                <span className="mb-2 block text-xs uppercase tracking-[0.2em] text-cyan-200/70">{String(item.memory_type ?? "memory")}</span>
                {String(item.content ?? "")}
              </div>
            ))}
          </div>
        </GlassCard>

        <GlassCard>
          <p className="section-label">Raw tracking history</p>
          <div className="mt-4 grid gap-3">
            {[
              `Workout logs: ${history?.workout_logs.length ?? 0}`,
              `Diet logs: ${history?.diet_logs.length ?? 0}`,
              `Progress logs: ${history?.progress_logs.length ?? 0}`,
              `Period logs: ${history?.period_logs.length ?? 0}`,
            ].map((item) => (
              <div key={item} className="rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white/70">
                {item}
              </div>
            ))}
          </div>
        </GlassCard>
      </div>
    </DashboardShell>
  );
}
