"use client";

import { useEffect, useMemo, useState } from "react";
import gsap from "gsap";
import { DashboardShell } from "@/components/dashboard-shell";
import { GlassCard } from "@/components/ui/glass-card";
import { StatCard } from "@/components/ui/stat-card";
import { GradientButton } from "@/components/ui/gradient-button";
import { useLocomotiveScroll } from "@/hooks/use-locomotive-scroll";
import { useAuroraSession } from "@/hooks/use-aurora-session";
import { backendRequest } from "@/lib/backend";
import type { HistoryResponse, ProgressSummary, WeeklyReport } from "@/lib/api-types";

const chartPoints = [20, 120, 220, 320, 420, 500];

export function ProgressScreen() {
  const { session, loading: sessionLoading, error: sessionError } = useAuroraSession();
  const [progress, setProgress] = useState<ProgressSummary | null>(null);
  const [weeklyReport, setWeeklyReport] = useState<WeeklyReport | null>(null);
  const [history, setHistory] = useState<HistoryResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useLocomotiveScroll(true);

  useEffect(() => {
    const ctx = gsap.context(() => {
      gsap.fromTo(
        ".progress-reveal",
        { opacity: 0, y: 30 },
        { opacity: 1, y: 0, stagger: 0.1, duration: 0.85, ease: "power3.out" },
      );
    });

    return () => ctx.revert();
  }, []);

  useEffect(() => {
    if (!session) {
      return;
    }

    const currentSession = session;

    let cancelled = false;

    async function loadProgress() {
      try {
        setLoading(true);
        setError(null);
        const [progressResponse, weeklyResponse, historyResponse] = await Promise.all([
          backendRequest<ProgressSummary>("/progress/me", currentSession.token),
          backendRequest<WeeklyReport>("/tracking/weekly-report", currentSession.token),
          backendRequest<HistoryResponse>("/tracking/history", currentSession.token),
        ]);

        if (!cancelled) {
          setProgress(progressResponse);
          setWeeklyReport(weeklyResponse);
          setHistory(historyResponse);
        }
      } catch (loadError) {
        if (!cancelled) {
          setError(loadError instanceof Error ? loadError.message : "Failed to load progress");
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    void loadProgress();

    return () => {
      cancelled = true;
    };
  }, [session]);

  async function handleSampleLog() {
    if (!session) {
      return;
    }

    try {
      setSubmitting(true);
      setError(null);

      await backendRequest("/progress/log", session.token, {
        method: "POST",
        body: JSON.stringify({
          energy_level: 8,
          mood: "focused",
          workout_minutes: 42,
          adherence_score: 8,
          notes: "Logged from the progress screen",
        }),
      });

      const [progressResponse, weeklyResponse, historyResponse] = await Promise.all([
        backendRequest<ProgressSummary>("/progress/me", session.token),
        backendRequest<WeeklyReport>("/tracking/weekly-report", session.token),
        backendRequest<HistoryResponse>("/tracking/history", session.token),
      ]);
      setProgress(progressResponse);
      setWeeklyReport(weeklyResponse);
      setHistory(historyResponse);
    } catch (submitError) {
      setError(submitError instanceof Error ? submitError.message : "Failed to log progress");
    } finally {
      setSubmitting(false);
    }
  }

  const recentLogs = progress?.history.slice(-6) ?? [];
  const volume = recentLogs.reduce((total, item) => total + item.workout_minutes, 0);
  const adherence = recentLogs.length > 0
    ? Math.round(recentLogs.reduce((total, item) => total + item.adherence_score, 0) / recentLogs.length * 10)
    : 0;
  const recovery = recentLogs.length > 0
    ? Math.round(recentLogs.reduce((total, item) => total + item.energy_level, 0) / recentLogs.length * 10)
    : 0;

  const chartYPoints = useMemo(() => {
    if (recentLogs.length === 0) {
      return [180, 160, 140, 120, 95, 70];
    }

    const source = recentLogs.slice(-chartPoints.length);
    const values = source.map((item) => item.energy_level * 10 + item.adherence_score * 3);
    const min = Math.min(...values);
    const max = Math.max(...values);
    return chartPoints.map((_, index) => {
      const value = values[index] ?? values[values.length - 1];
      const normalized = max === min ? 0.5 : (value - min) / (max - min);
      return Math.round(190 - normalized * 120);
    });
  }, [recentLogs]);

  const chartPath = chartPoints
    .map((x, index) => `${index === 0 ? "M" : "L"}${x} ${chartYPoints[index]}`)
    .join(" ");
  const chartArea = `${chartPath} L500 220 L20 220 Z`;

  return (
    <div data-scroll-container className="loco-scroll">
      <DashboardShell
        eyebrow="Progress"
        title="Measure momentum from real logs"
        description={sessionLoading ? "Creating your local Aurora session..." : "This page is now reading progress summaries, history, and weekly recommendations directly from the FastAPI backend."}
        headerStats={[
          { label: "Entries", value: `${progress?.entries ?? 0}` },
          { label: "Trend", value: progress?.trend ?? "no-data" },
          { label: "Window", value: weeklyReport ? `${weeklyReport.period_start} to ${weeklyReport.period_end}` : "this week" },
        ]}
      >
        {sessionError ? (
          <GlassCard className="progress-reveal">
            <h2 className="text-2xl font-semibold">Session failed</h2>
            <p className="mt-4 text-white/60">{sessionError}</p>
          </GlassCard>
        ) : null}

        {error ? (
          <GlassCard className="progress-reveal">
            <h2 className="text-2xl font-semibold">Progress error</h2>
            <p className="mt-4 text-white/60">{error}</p>
          </GlassCard>
        ) : null}

        <div className="grid gap-6">
          <section className="grid gap-6 md:grid-cols-3">
            <div className="progress-reveal">
              <StatCard label="Weekly volume" value={volume} suffix="m" detail="Total workout minutes across recent progress logs." accent="rgba(94,242,255,0.14)" />
            </div>
            <div className="progress-reveal">
              <StatCard label="Adherence" value={adherence} suffix="%" detail="Average adherence score from your recent logs." accent="rgba(134,93,255,0.16)" />
            </div>
            <div className="progress-reveal">
              <StatCard label="Recovery quality" value={recovery} suffix="%" detail="Energy-based recovery signal from recent logs." accent="rgba(140,255,122,0.12)" />
            </div>
          </section>

          <section className="grid gap-6 xl:grid-cols-[1.1fr,0.9fr]">
            <GlassCard className="progress-reveal overflow-hidden">
              <div className="flex items-start justify-between gap-4">
                <div>
                  <p className="section-label">Backend chart</p>
                  <h2 className="mt-3 text-3xl font-semibold">Performance arc</h2>
                  <p className="mt-3 max-w-2xl text-white/60">
                    {loading ? "Loading chart data from progress history..." : "The chart now maps recent progress logs instead of placeholder values."}
                  </p>
                </div>
                <GradientButton onClick={handleSampleLog} disabled={!session || submitting}>
                  {submitting ? "Logging..." : "Add Sample Log"}
                </GradientButton>
              </div>
              <div className="mt-8 h-72 rounded-[28px] border border-white/10 bg-white/5 p-5">
                <svg viewBox="0 0 520 240" className="h-full w-full">
                  <defs>
                    <linearGradient id="chartLine" x1="0%" x2="100%">
                      <stop offset="0%" stopColor="#865DFF" />
                      <stop offset="55%" stopColor="#5EF2FF" />
                      <stop offset="100%" stopColor="#8CFF7A" />
                    </linearGradient>
                  </defs>
                  <path d={chartPath} stroke="url(#chartLine)" strokeWidth="5" fill="none" strokeLinecap="round" />
                  <path d={chartArea} fill="url(#chartLine)" opacity="0.08" />
                  {chartPoints.map((x, index) => (
                    <circle key={`${x}-${chartYPoints[index]}`} cx={x} cy={chartYPoints[index]} r="7" fill="#5EF2FF" />
                  ))}
                </svg>
              </div>
            </GlassCard>

            <div className="grid gap-6">
              <GlassCard className="progress-reveal">
                <p className="section-label">Recent entries</p>
                <div className="mt-4 grid gap-3">
                  {(progress?.history.slice(-4).reverse() ?? []).map((item) => (
                    <div key={`${item.date}-${item.mood}`} className="rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white/70">
                      {item.date}: energy {item.energy_level}/10, adherence {item.adherence_score}/10, workout {item.workout_minutes} min
                    </div>
                  ))}
                  {!progress?.history.length ? (
                    <div className="rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white/70">
                      No progress logs yet. Use "Add Sample Log" to seed real backend data.
                    </div>
                  ) : null}
                </div>
              </GlassCard>

              <GlassCard className="progress-reveal shadow-[0_0_45px_rgba(94,242,255,0.18)]">
                <p className="section-label">Weekly insight</p>
                <h3 className="mt-3 text-2xl font-semibold">Aurora weekly report</h3>
                <p className="mt-4 text-white/70">
                  {weeklyReport?.summary ?? "Weekly report data will appear here once the session is loaded."}
                </p>
                <div className="mt-6 grid gap-3">
                  {(weeklyReport?.recommendations ?? history?.recent_memories.slice(0, 3).map((item) => String(item.content ?? "Memory saved")) ?? []).slice(0, 3).map((item) => (
                    <div key={item} className="rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white/70">
                      {item}
                    </div>
                  ))}
                </div>
              </GlassCard>
            </div>
          </section>
        </div>
      </DashboardShell>
    </div>
  );
}
