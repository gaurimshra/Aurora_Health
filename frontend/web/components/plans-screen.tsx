"use client";

import { useEffect, useState } from "react";
import { DashboardShell } from "@/components/dashboard-shell";
import { GlassCard } from "@/components/ui/glass-card";
import { GradientButton } from "@/components/ui/gradient-button";
import { useAuroraSession } from "@/hooks/use-aurora-session";
import { backendRequest, publicBackendRequest } from "@/lib/backend";
import type { PlanResponse, UserProfile } from "@/lib/api-types";

export function PlansScreen() {
  const { session, loading: sessionLoading, error: sessionError } = useAuroraSession();
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [plan, setPlan] = useState<PlanResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!session) return;
    void backendRequest<UserProfile>("/profile/me", session.token)
      .then(setProfile)
      .catch(() => undefined);
  }, [session]);

  async function generatePlan(formData: FormData) {
    try {
      setLoading(true);
      setError(null);
      const response = await publicBackendRequest<PlanResponse>("/generate-plan", {
        method: "POST",
        body: JSON.stringify({
          name: String(formData.get("name") ?? session?.name ?? "Aurora User"),
          age: Number(formData.get("age") ?? profile?.age ?? 26),
          gender: String(formData.get("gender") ?? profile?.gender ?? "female"),
          weight: Number(formData.get("weight") ?? profile?.weight ?? 62),
          height_cm: Number(formData.get("height_cm") ?? profile?.height_cm ?? 165),
          goal: String(formData.get("goal") ?? profile?.goal ?? "general fitness"),
          level: String(formData.get("level") ?? profile?.level ?? "beginner"),
          pregnant: formData.get("pregnant") === "true",
          postpartum: formData.get("postpartum") === "true",
          hormonal_concerns: String(formData.get("hormonal_concerns") ?? "").split(",").map((item) => item.trim()).filter(Boolean),
          dietary_restrictions: String(formData.get("dietary_restrictions") ?? "").split(",").map((item) => item.trim()).filter(Boolean),
          lifestyle: {
            sleep_hours: Number(formData.get("sleep_hours") ?? profile?.lifestyle?.sleep_hours ?? 7),
            water_liters: Number(formData.get("water_liters") ?? profile?.lifestyle?.water_liters ?? 2.5),
            stress_level: Number(formData.get("stress_level") ?? profile?.lifestyle?.stress_level ?? 5),
            activity_level: String(formData.get("activity_level") ?? profile?.lifestyle?.activity_level ?? "moderate"),
            dietary_preference: String(formData.get("dietary_preference") ?? profile?.lifestyle?.dietary_preference ?? "balanced"),
            health_goals: String(formData.get("health_goals") ?? profile?.lifestyle?.health_goals?.join(", ") ?? "")
              .split(",")
              .map((item) => item.trim())
              .filter(Boolean),
          },
        }),
      });
      setPlan(response);
    } catch (planError) {
      setError(planError instanceof Error ? planError.message : "Failed to generate plan");
    } finally {
      setLoading(false);
    }
  }

  return (
    <DashboardShell
      eyebrow="Plans"
      title="Backend plan generation"
      description={sessionLoading ? "Creating your local Aurora session..." : "This page is wired to the plan generator so workout, diet, and women’s-health guidance are produced from real form data."}
      headerStats={[
        { label: "Goal", value: profile?.goal ?? "General" },
        { label: "Level", value: profile?.level ?? "Beginner" },
        { label: "Plan", value: plan ? "Generated" : "Awaiting" },
      ]}
    >
      {sessionError ? <GlassCard><p className="text-white/70">{sessionError}</p></GlassCard> : null}
      {error ? <GlassCard><p className="text-white/70">{error}</p></GlassCard> : null}

      <div className="grid gap-6 xl:grid-cols-[0.9fr,1.1fr]">
        <GlassCard>
          <p className="section-label">Plan inputs</p>
          <h2 className="mt-3 text-2xl font-semibold">Generate a fresh Aurora plan</h2>
          <form action={generatePlan} className="mt-5 space-y-4">
            <div className="form-grid">
              <input className="input-shell" name="name" defaultValue={profile?.name ?? session?.name ?? ""} />
              <input className="input-shell" name="age" type="number" defaultValue={profile?.age ?? 26} />
              <input className="input-shell" name="gender" defaultValue={profile?.gender ?? "female"} />
              <input className="input-shell" name="weight" type="number" step="0.1" defaultValue={profile?.weight ?? 62} />
              <input className="input-shell" name="height_cm" type="number" step="0.1" defaultValue={profile?.height_cm ?? 165} />
              <input className="input-shell" name="goal" defaultValue={profile?.goal ?? "general fitness"} />
              <input className="input-shell" name="level" defaultValue={profile?.level ?? "beginner"} />
              <input className="input-shell" name="activity_level" defaultValue={profile?.lifestyle?.activity_level ?? "moderate"} />
              <input className="input-shell" name="dietary_preference" defaultValue={profile?.lifestyle?.dietary_preference ?? "balanced"} />
              <input className="input-shell" name="health_goals" defaultValue={profile?.lifestyle?.health_goals?.join(", ") ?? ""} />
              <input className="input-shell" name="sleep_hours" type="number" step="0.5" defaultValue={profile?.lifestyle?.sleep_hours ?? 7} />
              <input className="input-shell" name="water_liters" type="number" step="0.1" defaultValue={profile?.lifestyle?.water_liters ?? 2.5} />
              <input className="input-shell" name="stress_level" type="number" min="1" max="10" defaultValue={profile?.lifestyle?.stress_level ?? 5} />
              <input className="input-shell" name="hormonal_concerns" defaultValue={profile?.hormonal_concerns?.join(", ") ?? ""} />
              <input className="input-shell" name="dietary_restrictions" defaultValue={profile?.dietary_restrictions?.join(", ") ?? ""} />
              <select className="select-shell" name="pregnant" defaultValue={String(profile?.pregnant ?? false)}>
                <option value="false">Not pregnant</option>
                <option value="true">Pregnant</option>
              </select>
              <select className="select-shell" name="postpartum" defaultValue={String(profile?.postpartum ?? false)}>
                <option value="false">Not postpartum</option>
                <option value="true">Postpartum</option>
              </select>
            </div>
            <GradientButton type="submit" disabled={loading}>
              {loading ? "Generating..." : "Generate Plan"}
            </GradientButton>
          </form>
        </GlassCard>

        <div className="grid gap-6">
          <GlassCard>
            <p className="section-label">Workout plan</p>
            <p className="mt-4 text-white/70">{plan?.workout ?? "Generate a plan to see backend workout guidance."}</p>
          </GlassCard>
          <GlassCard>
            <p className="section-label">Diet plan</p>
            <p className="mt-4 text-white/70">{plan?.diet ?? "Generate a plan to see backend diet guidance."}</p>
          </GlassCard>
          <GlassCard>
            <p className="section-label">Women health guidance</p>
            <p className="mt-4 text-white/70">{plan?.women_health ?? "If the context is relevant, the backend will attach women’s-health guidance here."}</p>
          </GlassCard>
        </div>
      </div>
    </DashboardShell>
  );
}
