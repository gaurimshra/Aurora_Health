"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Flame, MoveUpRight, Zap } from "lucide-react";
import gsap from "gsap";
import { DashboardShell } from "@/components/dashboard-shell";
import { GlassCard } from "@/components/ui/glass-card";
import { StatCard } from "@/components/ui/stat-card";
import { GradientButton } from "@/components/ui/gradient-button";
import { useAuroraSession } from "@/hooks/use-aurora-session";
import { backendRequest } from "@/lib/backend";
import type { ProgressSummary, StreakSummary, UserProfile, WeeklyReport } from "@/lib/api-types";

type DashboardData = {
  profile: UserProfile | null;
  progress: ProgressSummary | null;
  streak: StreakSummary | null;
  weeklyReport: WeeklyReport | null;
};

export function DashboardOverview() {
  const { session, loading: sessionLoading, error: sessionError } = useAuroraSession();
  const [data, setData] = useState<DashboardData>({
    profile: null,
    progress: null,
    streak: null,
    weeklyReport: null,
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [checkinPending, setCheckinPending] = useState(false);

  useEffect(() => {
    const ctx = gsap.context(() => {
      gsap.fromTo(".dashboard-stagger", { opacity: 0, y: 22 }, { opacity: 1, y: 0, stagger: 0.08, duration: 0.8 });
    });
    return () => ctx.revert();
  }, []);

  useEffect(() => {
    if (!session) {
      return;
    }

    const currentSession = session;

    let cancelled = false;

    async function loadDashboard() {
      try {
        setLoading(true);
        setError(null);

        const [progress, streak, weeklyReport, profileResult] = await Promise.all([
          backendRequest<ProgressSummary>("/progress/me", currentSession.token),
          backendRequest<StreakSummary>("/streaks/me", currentSession.token),
          backendRequest<WeeklyReport>("/tracking/weekly-report", currentSession.token),
          backendRequest<UserProfile>("/profile/me", currentSession.token).catch(() => null),
        ]);

        if (!cancelled) {
          setData({ progress, streak, weeklyReport, profile: profileResult });
        }
      } catch (loadError) {
        if (!cancelled) {
          setError(loadError instanceof Error ? loadError.message : "Failed to load dashboard");
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    void loadDashboard();

    return () => {
      cancelled = true;
    };
  }, [session]);

  async function handleCheckIn() {
    if (!session) {
      return;
    }

    try {
      setCheckinPending(true);
      const updatedStreak = await backendRequest<StreakSummary>("/streaks/check-in", session.token, {
        method: "POST",
        body: JSON.stringify({
          workout_completed: true,
          nutrition_completed: false,
          journal_note: "Checked in from the dashboard",
        }),
      });
      setData((current) => ({ ...current, streak: updatedStreak }));
    } catch (checkinError) {
      setError(checkinError instanceof Error ? checkinError.message : "Failed to check in");
    } finally {
      setCheckinPending(false);
    }
  }

  const name = data.profile?.name ?? session?.name ?? "athlete";
  const latest = data.progress?.latest;
  const activeWorkout = data.weeklyReport?.recommendations[0] ?? "Log a workout to let Aurora build the next session.";
  const motivationItems = [
    data.streak?.motivation,
    data.weeklyReport?.wins[0],
    data.weeklyReport?.recommendations[1],
  ].filter(Boolean) as string[];

  return (
    <DashboardShell
      eyebrow="Dashboard"
      title={`Welcome back, ${name}`}
      description={sessionLoading ? "Creating your local Aurora session..." : "Aurora is now reading your real backend data and updating this dashboard from live profile, streak, and progress endpoints."}
      headerStats={[
        { label: "Mode", value: "Backend Connected" },
        { label: "Auth", value: "Local Session" },
        { label: "Trend", value: data.progress?.trend ?? "awaiting-data" },
      ]}
    >
      {sessionError ? (
        <GlassCard className="dashboard-stagger">
          <h2 className="text-2xl font-semibold">Session failed</h2>
          <p className="mt-4 text-white/60">{sessionError}</p>
        </GlassCard>
      ) : null}

      {error ? (
        <GlassCard className="dashboard-stagger">
          <h2 className="text-2xl font-semibold">Dashboard error</h2>
          <p className="mt-4 text-white/60">{error}</p>
        </GlassCard>
      ) : null}

      <div className="grid gap-6 xl:grid-cols-[1.2fr,0.8fr]">
        <div className="grid gap-6">
          <GlassCard className="dashboard-stagger overflow-hidden">
            <div className="flex flex-col gap-6 md:flex-row md:items-end md:justify-between">
              <div>
                <p className="section-label">Live status</p>
                <h2 className="mt-3 text-3xl md:text-4xl">
                  {loading ? "Loading your Aurora profile..." : "Your dashboard is running on real backend state."}
                </h2>
                <p className="mt-4 max-w-2xl text-white/60">
                  Goal: {data.profile?.goal ?? "not set"} · Level: {data.profile?.level ?? "not set"} · Progress trend: {data.progress?.trend ?? "no-data"}
                </p>
              </div>
              <GradientButton onClick={handleCheckIn} disabled={!session || checkinPending}>
                {checkinPending ? "Checking in..." : "Check In Today"}
              </GradientButton>
            </div>
          </GlassCard>

          <div className="grid gap-6 md:grid-cols-3">
            <div className="dashboard-stagger">
              <StatCard
                label="Current streak"
                value={data.streak?.current_streak ?? 0}
                suffix="d"
                detail={data.streak?.motivation ?? "Check in once to start building momentum."}
                accent="rgba(255,120,120,0.14)"
              />
            </div>
            <div className="dashboard-stagger">
              <StatCard
                label="Progress entries"
                value={data.progress?.entries ?? 0}
                detail={latest ? `Latest energy ${latest.energy_level}/10 with ${latest.workout_minutes} workout minutes.` : "No progress logs yet."}
                accent="rgba(94,242,255,0.14)"
              />
            </div>
            <div className="dashboard-stagger">
              <StatCard
                label="Adherence score"
                value={latest ? latest.adherence_score * 10 : 0}
                suffix="%"
                detail={latest ? `Mood: ${latest.mood}. Latest log on ${latest.date}.` : "Add a progress log to compute adherence."}
                accent="rgba(140,255,122,0.12)"
              />
            </div>
          </div>

          <GlassCard className="dashboard-stagger group overflow-hidden">
            <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_right,rgba(134,93,255,0.18),transparent_35%)] opacity-70 transition duration-500 group-hover:opacity-100" />
            <div className="relative flex flex-col gap-6 md:flex-row md:items-center md:justify-between">
              <div className="space-y-4">
                <div className="inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/10 px-3 py-1 text-xs text-white/60">
                  <Flame className="h-3.5 w-3.5 text-orange-300" />
                  Next recommendation
                </div>
                <div>
                  <h3 className="text-2xl font-semibold">{activeWorkout}</h3>
                  <p className="mt-3 max-w-xl text-white/60">
                    {data.weeklyReport?.summary ?? "Once workouts and progress logs are recorded, Aurora will generate a stronger weekly summary here."}
                  </p>
                </div>
              </div>
              <div className="grid gap-3 text-sm text-white/70">
                <div className="rounded-2xl border border-white/10 bg-white/5 px-4 py-3">Longest streak: {data.streak?.longest_streak ?? 0} days</div>
                <div className="rounded-2xl border border-white/10 bg-white/5 px-4 py-3">Last check-in: {data.streak?.last_checkin ?? "not yet"}</div>
                <div className="rounded-2xl border border-white/10 bg-white/5 px-4 py-3">Entries stored: {data.progress?.history.length ?? 0}</div>
              </div>
            </div>
          </GlassCard>
        </div>

        <div className="grid gap-6">
          <GlassCard className="dashboard-stagger">
            <div className="flex items-center justify-between">
              <div>
                <p className="section-label">Streak pulse</p>
                <h3 className="mt-2 text-2xl font-semibold">Momentum meter</h3>
              </div>
              <div className="rounded-full border border-orange-300/20 bg-orange-300/10 p-4 shadow-[0_0_40px_rgba(255,158,97,0.16)]">
                <Flame className="h-8 w-8 animate-pulse text-orange-300" />
              </div>
            </div>
            <div className="mt-6 grid gap-3">
              {(motivationItems.length > 0 ? motivationItems : ["Log a workout, add a progress entry, and check in to unlock recommendations."]).map((item) => (
                <div key={item} className="rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white/70">
                  {item}
                </div>
              ))}
            </div>
          </GlassCard>

          <GlassCard className="dashboard-stagger">
            <div className="flex items-start justify-between">
              <div>
                <p className="section-label">AI signal</p>
                <h3 className="mt-2 text-2xl font-semibold">Aurora recommendation</h3>
              </div>
              <Zap className="h-5 w-5 text-cyan-300" />
            </div>
            <p className="mt-5 text-white/70">
              {data.weeklyReport?.recommendations[0] ?? "Your backend is connected. The next step is adding workouts and progress logs so Aurora can respond with stronger guidance."}
            </p>
            <div className="mt-6 flex flex-wrap gap-3">
              <Link href="/workout">
                <GradientButton>Start Workout</GradientButton>
              </Link>
              <Link href="/progress">
                <GradientButton variant="ghost">
                  View Progress
                  <MoveUpRight className="h-4 w-4" />
                </GradientButton>
              </Link>
            </div>
          </GlassCard>
        </div>
      </div>
    </DashboardShell>
  );
}
