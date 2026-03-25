"use client";

import { useEffect, useState } from "react";
import { DashboardShell } from "@/components/dashboard-shell";
import { GlassCard } from "@/components/ui/glass-card";
import { GradientButton } from "@/components/ui/gradient-button";
import { useAuroraSession } from "@/hooks/use-aurora-session";
import { backendRequest } from "@/lib/backend";
import type { UserProfile } from "@/lib/api-types";

export function ProfileScreen() {
  const { session, loading: sessionLoading, error: sessionError } = useAuroraSession();
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (!session) return;
    const currentSession = session;
    void backendRequest<UserProfile>("/profile/me", currentSession.token)
      .then(setProfile)
      .catch(() => undefined);
  }, [session]);

  async function saveProfile(formData: FormData) {
    if (!session) return;
    try {
      setSaving(true);
      setError(null);
      const response = await backendRequest<{ profile: UserProfile }>("/profile", session.token, {
        method: "POST",
        body: JSON.stringify({
          name: String(formData.get("name") ?? session.name),
          age: Number(formData.get("age") ?? 26),
          gender: String(formData.get("gender") ?? "female"),
          weight: Number(formData.get("weight") ?? 62),
          height_cm: Number(formData.get("height_cm") ?? 165),
          goal: String(formData.get("goal") ?? "general fitness"),
          level: String(formData.get("level") ?? "beginner"),
          pregnant: formData.get("pregnant") === "true",
          postpartum: formData.get("postpartum") === "true",
          pregnancy_trimester: formData.get("pregnancy_trimester") ? Number(formData.get("pregnancy_trimester")) : null,
          postpartum_weeks: formData.get("postpartum_weeks") ? Number(formData.get("postpartum_weeks")) : null,
          hormonal_concerns: String(formData.get("hormonal_concerns") ?? "").split(",").map((item) => item.trim()).filter(Boolean),
          dietary_restrictions: String(formData.get("dietary_restrictions") ?? "").split(",").map((item) => item.trim()).filter(Boolean),
          lifestyle: {
            sleep_hours: Number(formData.get("sleep_hours") ?? 7),
            water_liters: Number(formData.get("water_liters") ?? 2.5),
            stress_level: Number(formData.get("stress_level") ?? 5),
            activity_level: String(formData.get("activity_level") ?? "moderate"),
            dietary_preference: String(formData.get("dietary_preference") ?? "balanced"),
            health_goals: String(formData.get("health_goals") ?? "").split(",").map((item) => item.trim()).filter(Boolean),
          },
        }),
      });
      setProfile(response.profile);
    } catch (saveError) {
      setError(saveError instanceof Error ? saveError.message : "Failed to save profile");
    } finally {
      setSaving(false);
    }
  }

  return (
    <DashboardShell
      eyebrow="Profile"
      title="Profile and health context"
      description={sessionLoading ? "Creating your local Aurora session..." : "This page writes to the backend profile endpoint so plans, progress coaching, and women’s health logic all have real user context."}
      headerStats={[
        { label: "Goal", value: profile?.goal ?? "Not set" },
        { label: "Level", value: profile?.level ?? "Not set" },
        { label: "Context", value: profile?.gender ?? "Unknown" },
      ]}
    >
      {sessionError ? <GlassCard><p className="text-white/70">{sessionError}</p></GlassCard> : null}
      {error ? <GlassCard><p className="text-white/70">{error}</p></GlassCard> : null}

      <GlassCard>
        <p className="section-label">Saved profile</p>
        <h2 className="mt-3 text-2xl font-semibold">Health and lifestyle baseline</h2>
        <form action={saveProfile} className="mt-5 space-y-4">
          <div className="form-grid">
            <input className="input-shell" name="name" placeholder="Name" defaultValue={profile?.name ?? session?.name ?? ""} />
            <input className="input-shell" name="age" type="number" min="13" defaultValue={profile?.age ?? 26} />
            <input className="input-shell" name="gender" placeholder="female, male, other" defaultValue={profile?.gender ?? "female"} />
            <input className="input-shell" name="goal" placeholder="general fitness, strength, fat loss" defaultValue={profile?.goal ?? "general fitness"} />
            <input className="input-shell" name="level" placeholder="beginner, intermediate, advanced" defaultValue={profile?.level ?? "beginner"} />
            <input className="input-shell" name="weight" type="number" min="20" step="0.1" defaultValue={profile?.weight ?? 62} />
            <input className="input-shell" name="height_cm" type="number" min="100" step="0.1" defaultValue={profile?.height_cm ?? 165} />
            <input className="input-shell" name="activity_level" placeholder="low, moderate, active" defaultValue={profile?.lifestyle?.activity_level ?? "moderate"} />
            <input className="input-shell" name="dietary_preference" placeholder="balanced, vegetarian, high-protein" defaultValue={profile?.lifestyle?.dietary_preference ?? "balanced"} />
            <input className="input-shell" name="health_goals" placeholder="better sleep, better energy" defaultValue={profile?.lifestyle?.health_goals?.join(", ") ?? ""} />
            <input className="input-shell" name="sleep_hours" type="number" step="0.5" defaultValue={profile?.lifestyle?.sleep_hours ?? 7} />
            <input className="input-shell" name="water_liters" type="number" step="0.1" defaultValue={profile?.lifestyle?.water_liters ?? 2.5} />
            <input className="input-shell" name="stress_level" type="number" min="1" max="10" defaultValue={profile?.lifestyle?.stress_level ?? 5} />
            <input className="input-shell" name="hormonal_concerns" placeholder="pcos, fatigue, thyroid" defaultValue={profile?.hormonal_concerns?.join(", ") ?? ""} />
            <input className="input-shell" name="dietary_restrictions" placeholder="vegetarian, lactose-free" defaultValue={profile?.dietary_restrictions?.join(", ") ?? ""} />
            <select className="select-shell" name="pregnant" defaultValue={String(profile?.pregnant ?? false)}>
              <option value="false">Not pregnant</option>
              <option value="true">Pregnant</option>
            </select>
            <select className="select-shell" name="postpartum" defaultValue={String(profile?.postpartum ?? false)}>
              <option value="false">Not postpartum</option>
              <option value="true">Postpartum</option>
            </select>
            <input className="input-shell" name="pregnancy_trimester" type="number" min="1" max="3" placeholder="Trimester" defaultValue={profile?.pregnancy_trimester ?? ""} />
            <input className="input-shell" name="postpartum_weeks" type="number" min="0" placeholder="Postpartum weeks" defaultValue={profile?.postpartum_weeks ?? ""} />
          </div>
          <GradientButton type="submit" disabled={!session || saving}>
            {saving ? "Saving..." : "Save Profile"}
          </GradientButton>
        </form>
      </GlassCard>
    </DashboardShell>
  );
}
