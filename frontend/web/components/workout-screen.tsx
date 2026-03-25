"use client";

import { useEffect, useMemo, useState } from "react";
import gsap from "gsap";
import { Camera, Circle, ScanSearch } from "lucide-react";
import { DashboardShell } from "@/components/dashboard-shell";
import { GlassCard } from "@/components/ui/glass-card";
import { AIFeedbackBox } from "@/components/ui/ai-feedback-box";
import { ProgressRing } from "@/components/ui/progress-ring";
import { GradientButton } from "@/components/ui/gradient-button";
import { useAuroraSession } from "@/hooks/use-aurora-session";
import { backendRequest } from "@/lib/backend";
import type { HistoryResponse, StreakSummary, WorkoutLog } from "@/lib/api-types";

const feedbackStates = [
  ["Shoulders stacked better now.", "Drive through the heel on the way up.", "Rep timing is clean. Keep breathing steady."],
  ["Core is engaging well.", "Tempo improved over the last 3 reps.", "Form score is rising. Stay controlled."],
  ["Knees are aligned.", "Good depth. Hold the bottom for half a beat.", "You look stable. Push for 2 more clean reps."],
];

export function WorkoutScreen() {
  const { session, loading: sessionLoading, error: sessionError } = useAuroraSession();
  const [active, setActive] = useState(true);
  const [repCount, setRepCount] = useState(12);
  const [feedbackIndex, setFeedbackIndex] = useState(0);
  const [history, setHistory] = useState<HistoryResponse | null>(null);
  const [streak, setStreak] = useState<StreakSummary | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);
  const feedback = useMemo(() => feedbackStates[feedbackIndex], [feedbackIndex]);

  useEffect(() => {
    const interval = window.setInterval(() => {
      setRepCount((value) => value + 1);
      setFeedbackIndex((value) => (value + 1) % feedbackStates.length);
    }, 3200);
    return () => window.clearInterval(interval);
  }, []);

  useEffect(() => {
    const ctx = gsap.context(() => {
      gsap.fromTo(".workout-reveal", { opacity: 0, y: 24 }, { opacity: 1, y: 0, stagger: 0.08, duration: 0.75 });
    });
    return () => ctx.revert();
  }, []);

  useEffect(() => {
    if (!session) {
      return;
    }

    const currentSession = session;

    let cancelled = false;

    async function loadWorkoutState() {
      try {
        setError(null);
        const [historyResponse, streakResponse] = await Promise.all([
          backendRequest<HistoryResponse>("/tracking/history", currentSession.token),
          backendRequest<StreakSummary>("/streaks/me", currentSession.token),
        ]);
        if (!cancelled) {
          setHistory(historyResponse);
          setStreak(streakResponse);
        }
      } catch (loadError) {
        if (!cancelled) {
          setError(loadError instanceof Error ? loadError.message : "Failed to load workout state");
        }
      }
    }

    void loadWorkoutState();

    return () => {
      cancelled = true;
    };
  }, [session]);

  async function handleSaveWorkout() {
    if (!session) {
      return;
    }

    try {
      setSaving(true);
      setError(null);

      await backendRequest<WorkoutLog>("/tracking/workout", session.token, {
        method: "POST",
        body: JSON.stringify({
          workout_type: "Lower body power + mobility flow",
          duration_minutes: repCount + 20,
          intensity: active ? "moderate-high" : "paused",
          completed: true,
          notes: `Captured from workout screen with ${repCount} live reps`,
        }),
      });

      const [historyResponse, streakResponse] = await Promise.all([
        backendRequest<HistoryResponse>("/tracking/history", session.token),
        backendRequest<StreakSummary>("/streaks/check-in", session.token, {
          method: "POST",
          body: JSON.stringify({
            workout_completed: true,
            nutrition_completed: false,
            journal_note: "Workout completed from the frontend workout screen",
          }),
        }),
      ]);

      setHistory(historyResponse);
      setStreak(streakResponse);
    } catch (saveError) {
      setError(saveError instanceof Error ? saveError.message : "Failed to save workout");
    } finally {
      setSaving(false);
    }
  }

  const recentWorkouts = history?.workout_logs.slice(0, 3) ?? [];
  const lastWorkout = recentWorkouts[0];
  const formScore = Math.min(99, 68 + repCount);

  return (
    <DashboardShell
      eyebrow="Workout Mode"
      title="Realtime training intelligence"
      description={sessionLoading ? "Creating your local Aurora session..." : "Workout logs and streak check-ins now persist to the backend instead of staying as frontend-only placeholders."}
      headerStats={[
        { label: "Live reps", value: `${repCount}` },
        { label: "Stored workouts", value: `${history?.workout_logs.length ?? 0}` },
        { label: "Streak", value: `${streak?.current_streak ?? 0} days` },
      ]}
    >
      {sessionError ? (
        <GlassCard className="workout-reveal">
          <h2 className="text-2xl font-semibold">Session failed</h2>
          <p className="mt-4 text-white/60">{sessionError}</p>
        </GlassCard>
      ) : null}

      {error ? (
        <GlassCard className="workout-reveal">
          <h2 className="text-2xl font-semibold">Workout error</h2>
          <p className="mt-4 text-white/60">{error}</p>
        </GlassCard>
      ) : null}

      <div className="grid gap-6 xl:grid-cols-[1.15fr,0.85fr]">
        <GlassCard className="workout-reveal relative min-h-[640px] overflow-hidden">
          <div className="absolute inset-0 bg-[radial-gradient(circle_at_top,rgba(94,242,255,0.1),transparent_34%)]" />
          <div className="relative flex h-full flex-col justify-between">
            <div className="flex items-center justify-between">
              <div>
                <p className="section-label">Computer vision surface</p>
                <h2 className="mt-3 text-3xl font-semibold">Webcam + pose layer</h2>
              </div>
              <button
                type="button"
                onClick={() => setActive((value) => !value)}
                className="rounded-full border border-white/10 bg-white/10 px-4 py-2 text-sm text-white/70"
              >
                {active ? "Pause glow" : "Activate glow"}
              </button>
            </div>

            <div className="relative mt-6 flex-1 overflow-hidden rounded-[32px] border border-white/10 bg-[#05070f]">
              <div className={`absolute inset-0 transition duration-700 ${active ? "bg-cyan-400/10" : "bg-transparent"}`} />
              <div className="absolute inset-6 rounded-[28px] border border-dashed border-cyan-300/20" />
              <div className="absolute left-6 top-6 flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-3 py-2 text-xs text-white/60">
                <Camera className="h-4 w-4" />
                Camera feed placeholder
              </div>
              <div className="absolute right-6 top-6 flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-3 py-2 text-xs text-white/60">
                <ScanSearch className="h-4 w-4" />
                Skeleton overlay placeholder
              </div>
              <div className="absolute inset-x-0 top-1/4 flex justify-center">
                <div className={`relative ${active ? "animate-pulseSoft" : ""}`}>
                  <div className="h-80 w-80 rounded-full border border-cyan-300/20 bg-[radial-gradient(circle,rgba(94,242,255,0.18),transparent_58%)] blur-2xl" />
                  <div className="absolute inset-0 flex items-center justify-center">
                    <Circle className="h-44 w-44 text-cyan-200/30" strokeWidth={1} />
                  </div>
                </div>
              </div>
              {[
                "Head",
                "Shoulders",
                "Hips",
                "Knees",
              ].map((joint, index) => (
                <div
                  key={joint}
                  className="absolute flex items-center gap-2 rounded-full border border-cyan-300/20 bg-cyan-300/10 px-3 py-1 text-xs text-cyan-100/70"
                  style={{
                    left: `${22 + index * 13}%`,
                    top: `${18 + index * 14}%`,
                  }}
                >
                  <span className="h-2 w-2 rounded-full bg-cyan-200" />
                  {joint}
                </div>
              ))}
            </div>
          </div>
        </GlassCard>

        <div className="grid gap-6">
          <AIFeedbackBox title="Realtime feedback" feedback={feedback} />

          <div className="grid gap-6 md:grid-cols-2 xl:grid-cols-1">
            <GlassCard className="workout-reveal">
              <p className="section-label">Rep counter</p>
              <div className="mt-4 flex items-end justify-between">
                <div>
                  <div className="text-6xl font-semibold text-white">{repCount}</div>
                  <p className="mt-2 text-white/60">
                    {lastWorkout ? `Last saved workout: ${lastWorkout.workout_type} for ${lastWorkout.duration_minutes} min.` : "Save a workout to persist this session to the backend."}
                  </p>
                </div>
                <div className="rounded-full border border-emerald-300/20 bg-emerald-300/10 px-4 py-2 text-sm text-emerald-200">
                  {active ? "active" : "paused"}
                </div>
              </div>
            </GlassCard>

            <GlassCard className="workout-reveal flex items-center justify-center">
              <ProgressRing value={formScore} label="Form Score" />
            </GlassCard>
          </div>

          <GlassCard className="workout-reveal">
            <div className="flex items-center justify-between gap-4">
              <p className="section-label">Live cues</p>
              <GradientButton onClick={handleSaveWorkout} disabled={!session || saving}>
                {saving ? "Saving..." : "Save Workout"}
              </GradientButton>
            </div>
            <div className="mt-4 grid gap-3">
              {(recentWorkouts.length > 0
                ? recentWorkouts.map((item) => `${item.date}: ${item.workout_type} · ${item.duration_minutes} min · ${item.intensity}`)
                : [
                    "Depth locked in",
                    "Breathing rhythm stable",
                    "Left-right balance improved",
                  ]).map((item) => (
                <div key={item} className="rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white/70">
                  {item}
                </div>
              ))}
            </div>
            <p className="mt-4 text-white/60">
              {streak?.motivation ?? "Complete one workout and Aurora will attach it to your streak automatically."}
            </p>
          </GlassCard>
        </div>
      </div>
    </DashboardShell>
  );
}
