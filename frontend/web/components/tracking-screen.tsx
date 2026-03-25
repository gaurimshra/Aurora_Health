"use client";

import { useEffect, useState } from "react";
import { DashboardShell } from "@/components/dashboard-shell";
import { GlassCard } from "@/components/ui/glass-card";
import { GradientButton } from "@/components/ui/gradient-button";
import { useAuroraSession } from "@/hooks/use-aurora-session";
import { backendRequest } from "@/lib/backend";
import type { DietLog, HistoryResponse, WorkoutLog } from "@/lib/api-types";

export function TrackingScreen() {
  const { session, loading: sessionLoading, error: sessionError } = useAuroraSession();
  const [history, setHistory] = useState<HistoryResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState<string | null>(null);

  useEffect(() => {
    if (!session) return;
    const currentSession = session;

    void backendRequest<HistoryResponse>("/tracking/history", currentSession.token)
      .then(setHistory)
      .catch((loadError) => setError(loadError instanceof Error ? loadError.message : "Failed to load tracking history"));
  }, [session]);

  async function refreshHistory() {
    if (!session) return;
    const nextHistory = await backendRequest<HistoryResponse>("/tracking/history", session.token);
    setHistory(nextHistory);
  }

  async function submitWorkout(formData: FormData) {
    if (!session) return;
    try {
      setSaving("workout");
      setError(null);
      await backendRequest<WorkoutLog>("/tracking/workout", session.token, {
        method: "POST",
        body: JSON.stringify({
          workout_type: String(formData.get("workout_type") ?? "strength"),
          duration_minutes: Number(formData.get("duration_minutes") ?? 30),
          intensity: String(formData.get("intensity") ?? "moderate"),
          completed: formData.get("completed") === "true",
          notes: String(formData.get("workout_notes") ?? ""),
        }),
      });
      await refreshHistory();
    } catch (submitError) {
      setError(submitError instanceof Error ? submitError.message : "Failed to save workout log");
    } finally {
      setSaving(null);
    }
  }

  async function submitDiet(formData: FormData) {
    if (!session) return;
    try {
      setSaving("diet");
      setError(null);
      await backendRequest<DietLog>("/tracking/diet", session.token, {
        method: "POST",
        body: JSON.stringify({
          meals_followed: Number(formData.get("meals_followed") ?? 3),
          hydration_liters: Number(formData.get("hydration_liters") ?? 2),
          protein_grams: Number(formData.get("protein_grams") ?? 90),
          cravings: String(formData.get("cravings") ?? "")
            .split(",")
            .map((item) => item.trim())
            .filter(Boolean),
          notes: String(formData.get("diet_notes") ?? ""),
        }),
      });
      await refreshHistory();
    } catch (submitError) {
      setError(submitError instanceof Error ? submitError.message : "Failed to save diet log");
    } finally {
      setSaving(null);
    }
  }

  async function submitFeedback(formData: FormData) {
    if (!session) return;
    try {
      setSaving("feedback");
      setError(null);
      await backendRequest("/tracking/feedback", session.token, {
        method: "POST",
        body: JSON.stringify({
          category: String(formData.get("category") ?? "app experience"),
          feedback: String(formData.get("feedback") ?? ""),
          rating: Number(formData.get("rating") ?? 7),
        }),
      });
      await refreshHistory();
    } catch (submitError) {
      setError(submitError instanceof Error ? submitError.message : "Failed to save feedback");
    } finally {
      setSaving(null);
    }
  }

  return (
    <DashboardShell
      eyebrow="Tracking"
      title="Daily tracking inputs"
      description={sessionLoading ? "Creating your local Aurora session..." : "These forms write directly to the workout, diet, and feedback endpoints so the app has real input data to work with."}
      headerStats={[
        { label: "Workouts", value: `${history?.workout_logs.length ?? 0}` },
        { label: "Diet Logs", value: `${history?.diet_logs.length ?? 0}` },
        { label: "Memories", value: `${history?.recent_memories.length ?? 0}` },
      ]}
    >
      {sessionError ? <GlassCard><p className="text-white/70">{sessionError}</p></GlassCard> : null}
      {error ? <GlassCard><p className="text-white/70">{error}</p></GlassCard> : null}

      <div className="grid gap-6 xl:grid-cols-3">
        <GlassCard>
          <p className="section-label">Workout log</p>
          <h2 className="mt-3 text-2xl font-semibold">Capture a session</h2>
          <form action={submitWorkout} className="mt-5 space-y-4">
            <input className="input-shell" name="workout_type" placeholder="strength, cardio, mobility" defaultValue="strength" />
            <input className="input-shell" name="duration_minutes" type="number" min="0" defaultValue="40" />
            <select className="select-shell" name="intensity" defaultValue="moderate">
              <option value="low">Low</option>
              <option value="moderate">Moderate</option>
              <option value="high">High</option>
            </select>
            <select className="select-shell" name="completed" defaultValue="true">
              <option value="true">Completed</option>
              <option value="false">Not completed</option>
            </select>
            <textarea className="textarea-shell" name="workout_notes" placeholder="Energy, pain points, exercises, soreness" />
            <GradientButton className="w-full" type="submit" disabled={!session || saving === "workout"}>
              {saving === "workout" ? "Saving..." : "Save Workout"}
            </GradientButton>
          </form>
        </GlassCard>

        <GlassCard>
          <p className="section-label">Diet log</p>
          <h2 className="mt-3 text-2xl font-semibold">Capture nutrition context</h2>
          <form action={submitDiet} className="mt-5 space-y-4">
            <input className="input-shell" name="meals_followed" type="number" min="0" max="10" defaultValue="3" />
            <input className="input-shell" name="hydration_liters" type="number" min="0" step="0.1" defaultValue="2.4" />
            <input className="input-shell" name="protein_grams" type="number" min="0" defaultValue="90" />
            <input className="input-shell" name="cravings" placeholder="sweet, salty, carbs" />
            <textarea className="textarea-shell" name="diet_notes" placeholder="Meal quality, digestion, hunger, supplements" />
            <GradientButton className="w-full" type="submit" disabled={!session || saving === "diet"}>
              {saving === "diet" ? "Saving..." : "Save Diet"}
            </GradientButton>
          </form>
        </GlassCard>

        <GlassCard>
          <p className="section-label">Feedback memory</p>
          <h2 className="mt-3 text-2xl font-semibold">Teach Aurora what worked</h2>
          <form action={submitFeedback} className="mt-5 space-y-4">
            <input className="input-shell" name="category" placeholder="plan, coach, cycle, diet, app experience" defaultValue="app experience" />
            <input className="input-shell" name="rating" type="number" min="1" max="10" defaultValue="8" />
            <textarea className="textarea-shell" name="feedback" placeholder="What should Aurora keep, change, or remember?" />
            <GradientButton className="w-full" type="submit" disabled={!session || saving === "feedback"}>
              {saving === "feedback" ? "Saving..." : "Save Feedback"}
            </GradientButton>
          </form>
        </GlassCard>
      </div>

      <div className="grid gap-6 xl:grid-cols-2">
        <GlassCard>
          <p className="section-label">Recent workouts</p>
          <div className="mt-4 grid gap-3">
            {(history?.workout_logs.slice(0, 5) ?? []).map((item) => (
              <div key={`${item.date}-${item.workout_type}-${item.duration_minutes}`} className="rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white/70">
                {item.date}: {item.workout_type} · {item.duration_minutes} min · {item.intensity}
              </div>
            ))}
            {!history?.workout_logs.length ? <div className="rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white/70">No workout logs yet.</div> : null}
          </div>
        </GlassCard>

        <GlassCard>
          <p className="section-label">Recent diet logs</p>
          <div className="mt-4 grid gap-3">
            {(history?.diet_logs.slice(0, 5) ?? []).map((item) => (
              <div key={`${item.date}-${item.meals_followed}-${item.hydration_liters}`} className="rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white/70">
                {item.date}: meals {item.meals_followed} · hydration {item.hydration_liters}L · protein {item.protein_grams ?? 0}g
              </div>
            ))}
            {!history?.diet_logs.length ? <div className="rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white/70">No diet logs yet.</div> : null}
          </div>
        </GlassCard>
      </div>
    </DashboardShell>
  );
}
