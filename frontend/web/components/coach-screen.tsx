"use client";

import { useState } from "react";
import { DashboardShell } from "@/components/dashboard-shell";
import { GlassCard } from "@/components/ui/glass-card";
import { GradientButton } from "@/components/ui/gradient-button";
import { useAuroraSession } from "@/hooks/use-aurora-session";
import { backendRequest } from "@/lib/backend";
import type { CoachResponse } from "@/lib/api-types";

export function CoachScreen() {
  const { session, loading: sessionLoading, error: sessionError } = useAuroraSession();
  const [coach, setCoach] = useState<CoachResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function askCoach(formData: FormData) {
    if (!session) return;
    try {
      setLoading(true);
      setError(null);
      const response = await backendRequest<CoachResponse>("/progress/coach", session.token, {
        method: "POST",
        body: JSON.stringify({
          message: String(formData.get("message") ?? ""),
        }),
      });
      setCoach(response);
    } catch (coachError) {
      setError(coachError instanceof Error ? coachError.message : "Failed to get coach response");
    } finally {
      setLoading(false);
    }
  }

  return (
    <DashboardShell
      eyebrow="Coach"
      title="Memory-backed coaching"
      description={sessionLoading ? "Creating your local Aurora session..." : "This screen uses the backend progress coach endpoint so replies are grounded in stored profile, logs, and memory retrieval."}
      headerStats={[
        { label: "Mode", value: "Progress Coach" },
        { label: "Memory", value: "Enabled" },
        { label: "Reply", value: coach ? "Loaded" : "Awaiting" },
      ]}
    >
      {sessionError ? <GlassCard><p className="text-white/70">{sessionError}</p></GlassCard> : null}
      {error ? <GlassCard><p className="text-white/70">{error}</p></GlassCard> : null}

      <div className="grid gap-6 xl:grid-cols-[0.9fr,1.1fr]">
        <GlassCard>
          <p className="section-label">Ask Aurora</p>
          <h2 className="mt-3 text-2xl font-semibold">Coach console</h2>
          <form action={askCoach} className="mt-5 space-y-4">
            <textarea className="textarea-shell" name="message" placeholder="I lose consistency after two good days. How should I structure the next week?" />
            <GradientButton className="w-full" type="submit" disabled={!session || loading}>
              {loading ? "Thinking..." : "Get Coaching"}
            </GradientButton>
          </form>
        </GlassCard>

        <GlassCard>
          <p className="section-label">Coach response</p>
          <h2 className="mt-3 text-2xl font-semibold">Aurora reply</h2>
          <p className="mt-4 text-white/70">{coach?.reply ?? "Ask a question to generate a backend-backed coaching response."}</p>

          {coach?.insights?.length ? (
            <>
              <p className="section-label mt-6">Insights</p>
              <div className="mt-3 grid gap-3">
                {coach.insights.map((item) => (
                  <div key={item} className="rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white/70">{item}</div>
                ))}
              </div>
            </>
          ) : null}

          {coach?.next_steps?.length ? (
            <>
              <p className="section-label mt-6">Next steps</p>
              <div className="mt-3 grid gap-3">
                {coach.next_steps.map((item) => (
                  <div key={item} className="rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white/70">{item}</div>
                ))}
              </div>
            </>
          ) : null}
        </GlassCard>
      </div>
    </DashboardShell>
  );
}
