"use client";

import { useEffect, useState } from "react";
import { DashboardShell } from "@/components/dashboard-shell";
import { GlassCard } from "@/components/ui/glass-card";
import { GradientButton } from "@/components/ui/gradient-button";
import { useAuroraSession } from "@/hooks/use-aurora-session";
import { backendRequest } from "@/lib/backend";
import type { WomenHealthDashboard } from "@/lib/api-types";

export function WomenHealthScreen() {
  const { session, loading: sessionLoading, error: sessionError } = useAuroraSession();
  const [dashboard, setDashboard] = useState<WomenHealthDashboard | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (!session) return;
    void backendRequest<WomenHealthDashboard>("/women-health/dashboard", session.token)
      .then(setDashboard)
      .catch((loadError) => setError(loadError instanceof Error ? loadError.message : "Failed to load women health dashboard"));
  }, [session]);

  async function savePeriod(formData: FormData) {
    if (!session) return;
    try {
      setSaving(true);
      setError(null);
      await backendRequest("/women-health/log-period", session.token, {
        method: "POST",
        body: JSON.stringify({
          start_date: String(formData.get("start_date") ?? ""),
          end_date: String(formData.get("end_date") ?? ""),
          symptoms: String(formData.get("symptoms") ?? "").split(",").map((item) => item.trim()).filter(Boolean),
          flow_level: String(formData.get("flow_level") ?? "moderate"),
          mood: String(formData.get("mood") ?? "stable"),
          cravings: String(formData.get("cravings") ?? "").split(",").map((item) => item.trim()).filter(Boolean),
          notes: String(formData.get("notes") ?? ""),
        }),
      });
      const nextDashboard = await backendRequest<WomenHealthDashboard>("/women-health/dashboard", session.token);
      setDashboard(nextDashboard);
    } catch (saveError) {
      setError(saveError instanceof Error ? saveError.message : "Failed to save period log");
    } finally {
      setSaving(false);
    }
  }

  return (
    <DashboardShell
      eyebrow="Women Health"
      title="Cycle-aware tracking"
      description={sessionLoading ? "Creating your local Aurora session..." : "This page connects directly to the period logging and women’s-health dashboard endpoints so the cycle-aware backend guidance is visible in the web app too."}
      headerStats={[
        { label: "Phase", value: dashboard?.predicted_phase ?? "Unknown" },
        { label: "Cycle", value: dashboard?.average_cycle_length ? `${dashboard.average_cycle_length}d` : "n/a" },
        { label: "Irregularity", value: dashboard?.irregularity_score ?? "Unknown" },
      ]}
    >
      {sessionError ? <GlassCard><p className="text-white/70">{sessionError}</p></GlassCard> : null}
      {error ? <GlassCard><p className="text-white/70">{error}</p></GlassCard> : null}

      <div className="grid gap-6 xl:grid-cols-[0.9fr,1.1fr]">
        <GlassCard>
          <p className="section-label">Period log</p>
          <h2 className="mt-3 text-2xl font-semibold">Save cycle data</h2>
          <form action={savePeriod} className="mt-5 space-y-4">
            <input className="input-shell" name="start_date" type="date" />
            <input className="input-shell" name="end_date" type="date" />
            <input className="input-shell" name="symptoms" placeholder="cramps, fatigue, acne, mood swings" />
            <input className="input-shell" name="cravings" placeholder="sweet, salty, carbs" />
            <select className="select-shell" name="flow_level" defaultValue="moderate">
              <option value="light">Light</option>
              <option value="moderate">Moderate</option>
              <option value="heavy">Heavy</option>
            </select>
            <input className="input-shell" name="mood" placeholder="stable, low, irritable, energized" defaultValue="stable" />
            <textarea className="textarea-shell" name="notes" placeholder="Anything Aurora should keep in context for future recommendations" />
            <GradientButton className="w-full" type="submit" disabled={!session || saving}>
              {saving ? "Saving..." : "Save Period Log"}
            </GradientButton>
          </form>
        </GlassCard>

        <div className="grid gap-6">
          <GlassCard>
            <p className="section-label">Cycle dashboard</p>
            <div className="mt-4 grid gap-3">
              {[
                `Predicted phase: ${dashboard?.predicted_phase ?? "unknown"}`,
                `Next period start: ${dashboard?.next_period_start ?? "unknown"}`,
                `Average period length: ${dashboard?.average_period_length ?? "n/a"}`,
              ].map((item) => (
                <div key={item} className="rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white/70">{item}</div>
              ))}
            </div>
          </GlassCard>
          <GlassCard>
            <p className="section-label">Nutrition focus</p>
            <div className="mt-4 grid gap-3">
              {(dashboard?.nutrition_focus ?? []).map((item) => (
                <div key={item} className="rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white/70">{item}</div>
              ))}
            </div>
          </GlassCard>
          <GlassCard>
            <p className="section-label">Workout focus</p>
            <div className="mt-4 grid gap-3">
              {(dashboard?.workout_focus ?? []).map((item) => (
                <div key={item} className="rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white/70">{item}</div>
              ))}
            </div>
            {dashboard?.disclaimer ? <p className="mt-4 text-sm text-white/50">{dashboard.disclaimer}</p> : null}
          </GlassCard>
        </div>
      </div>
    </DashboardShell>
  );
}
