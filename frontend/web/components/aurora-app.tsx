"use client";

import Link from "next/link";
import { useCallback, useEffect, useMemo, useState, useTransition } from "react";
import type { Dispatch, ReactNode, SetStateAction } from "react";
import {
  Activity,
  ArrowRight,
  Brain,
  CalendarRange,
  Dumbbell,
  HeartPulse,
  LayoutDashboard,
  LoaderCircle,
  LogOut,
  MessageSquareText,
  MoonStar,
  Salad,
  ShieldPlus,
  Sparkles,
  Target,
  TrendingUp,
  UserRound,
  X,
} from "lucide-react";
import { backendRequest, publicBackendRequest } from "@/lib/backend";
import type {
  CoachResponse,
  HistoryResponse,
  PlanResponse,
  ProgressSummary,
  StreakSummary,
  UserProfile,
  WeeklyReport,
  WomenHealthDashboard,
} from "@/lib/api-types";
import {
  clearStoredSession,
  getStoredSession,
  loginLocalSession,
  type AuroraSession,
  registerLocalSession,
} from "@/lib/local-session";

type SectionKey =
  | "home"
  | "profile"
  | "plans"
  | "tracking"
  | "progress"
  | "women-health"
  | "memory"
  | "reports"
  | "coach";

type DashboardBundle = {
  progress: ProgressSummary;
  streak: StreakSummary;
  history: HistoryResponse;
  weeklyReport: WeeklyReport;
  womenHealth: WomenHealthDashboard;
};

type AssistantMessage = {
  role: "assistant" | "user";
  content: string;
};

type WorkoutFormState = ReturnType<typeof buildWorkoutForm>;
type DietFormState = ReturnType<typeof buildDietForm>;
type ProgressFormState = ReturnType<typeof buildProgressForm>;
type CheckinFormState = ReturnType<typeof buildCheckinForm>;
type FeedbackFormState = ReturnType<typeof buildFeedbackForm>;
type PeriodFormState = ReturnType<typeof buildPeriodForm>;

const navItems: Array<{
  key: SectionKey;
  label: string;
  href: string;
  icon: typeof LayoutDashboard;
  description: string;
}> = [
  { key: "home", label: "Home", href: "/", icon: LayoutDashboard, description: "Overview, live workspace, and smart summaries." },
  { key: "profile", label: "Profile", href: "/profile", icon: UserRound, description: "Personal details, goals, and lifestyle preferences." },
  { key: "plans", label: "Plans", href: "/plans", icon: Target, description: "Workout, diet, and women-first plan generation." },
  { key: "tracking", label: "Daily Tracking", href: "/tracking", icon: Activity, description: "Workout, diet, feedback, and daily check-in logs." },
  { key: "progress", label: "Progress", href: "/progress", icon: TrendingUp, description: "Energy, adherence, mood, and workout progress." },
  { key: "women-health", label: "Women's Health", href: "/women-health", icon: HeartPulse, description: "Cycle tracking, symptoms, and recovery guidance." },
  { key: "memory", label: "Memory & History", href: "/memory", icon: Brain, description: "Recent memories, search, and long-term activity history." },
  { key: "reports", label: "Weekly Report", href: "/reports", icon: CalendarRange, description: "Wins, risks, and recommendations from Aurora." },
  { key: "coach", label: "Aurora Coach", href: "/coach", icon: MessageSquareText, description: "Ask Aurora for guidance and next steps." },
];

const sectionPrompts: Record<SectionKey, string[]> = {
  home: ["What should I focus on today?", "Explain my dashboard quickly."],
  profile: ["How do I fill this profile correctly?", "What details improve personalization?"],
  plans: ["Build a practical plan for me.", "How should I use my generated plan?"],
  tracking: ["What should I log every day?", "How do I keep tracking simple?"],
  progress: ["Explain my progress trend.", "What should I improve this week?"],
  "women-health": ["How should I use the cycle tracker?", "What does my current phase mean?"],
  memory: ["What is stored in memory?", "How can memory improve coaching?"],
  reports: ["Summarize my weekly report.", "What should I act on first?"],
  coach: ["Give me three next steps.", "Help me stay consistent this week."],
};

const emptyProgress: ProgressSummary = { user_id: "", entries: 0, trend: "no-data", latest: null, history: [] };
const emptyStreak: StreakSummary = {
  user_id: "",
  current_streak: 0,
  longest_streak: 0,
  total_checkins: 0,
  motivation: "Start with today. Consistency matters more than intensity.",
  last_checkin: null,
};
const emptyHistory: HistoryResponse = { workout_logs: [], diet_logs: [], progress_logs: [], period_logs: [], recent_memories: [] };
const emptyWeeklyReport: WeeklyReport = {
  user_id: "",
  period_start: "",
  period_end: "",
  summary: "No weekly report yet. Start logging your workouts, food, progress, and recovery patterns.",
  wins: [],
  risks: [],
  recommendations: [],
};
const emptyWomenHealth: WomenHealthDashboard = {
  user_id: "",
  average_cycle_length: null,
  average_period_length: null,
  next_period_start: null,
  predicted_phase: "insufficient-data",
  irregularity_score: "unknown",
  recent_logs: [],
  possible_concerns: [],
  nutrition_focus: [],
  workout_focus: [],
  disclaimer: "This section becomes more useful after you add period logs and profile context.",
};

const defaultProfile: UserProfile = {
  name: "",
  age: 25,
  gender: "female",
  weight: 60,
  height_cm: 165,
  goal: "Build strength and improve energy",
  level: "beginner",
  pregnant: false,
  postpartum: false,
  pregnancy_trimester: null,
  postpartum_weeks: null,
  hormonal_concerns: [],
  dietary_restrictions: [],
  lifestyle: {
    sleep_hours: 7,
    water_liters: 2.5,
    stress_level: 5,
    activity_level: "moderate",
    dietary_preference: "balanced",
    health_goals: ["better energy", "consistency"],
  },
};

const today = () => new Date().toISOString().slice(0, 10);

function buildWorkoutForm() {
  return { date: today(), workout_type: "Strength training", duration_minutes: 40, intensity: "moderate", completed: true, notes: "" };
}

function buildDietForm() {
  return { date: today(), meals_followed: 3, hydration_liters: 2.5, protein_grams: 90 as number | null, cravings: "coffee, sweets", notes: "" };
}

function buildProgressForm() {
  return { date: today(), weight: 60 as number | null, energy_level: 7, mood: "Focused", workout_minutes: 40, adherence_score: 8, notes: "" };
}

function buildCheckinForm() {
  return { date: today(), workout_completed: true, nutrition_completed: true, journal_note: "" };
}

function buildFeedbackForm() {
  return { category: "home dashboard", feedback: "", rating: 8 as number | null };
}

function buildPeriodForm() {
  return { start_date: today(), end_date: today(), symptoms: "cramps, fatigue", flow_level: "moderate", mood: "stable", cravings: "chocolate", notes: "" };
}

function parseList(value: string) {
  return value.split(",").map((item) => item.trim()).filter(Boolean);
}

function listToText(value: string[] | undefined) {
  return (value ?? []).join(", ");
}

function formatDate(value?: string | null) {
  if (!value) return "Not available";
  try {
    return new Intl.DateTimeFormat("en-US", { month: "short", day: "numeric", year: "numeric" }).format(new Date(value));
  } catch {
    return value;
  }
}

function formatNumber(value?: number | null, suffix = "") {
  if (value === undefined || value === null || Number.isNaN(value)) return "--";
  return `${value}${suffix}`;
}

function normalizeError(error: unknown) {
  if (error instanceof Error) return error.message;
  return "Something went wrong. Try again.";
}

function compactText(value: string | null | undefined) {
  return value && value.trim() ? value.trim() : "No data yet.";
}

function scoreLabel(value: string) {
  return value.split("-").map((part) => part.charAt(0).toUpperCase() + part.slice(1)).join(" ");
}

function useProfileDraft(profile: UserProfile | null, session: AuroraSession | null) {
  const [draft, setDraft] = useState<UserProfile>(defaultProfile);

  useEffect(() => {
    if (profile) {
      setDraft(profile);
      return;
    }
    setDraft((current) => ({ ...current, name: session?.name ?? current.name }));
  }, [profile, session]);

  return [draft, setDraft] as const;
}

function EmptyState({ title, text }: { title: string; text: string }) {
  return (
    <div className="rounded-[24px] border border-dashed border-slate-200 bg-slate-50 px-5 py-6">
      <p className="font-semibold text-slate-900">{title}</p>
      <p className="mt-2 text-sm leading-6 text-slate-500">{text}</p>
    </div>
  );
}

function StatusNotice({ text, tone = "neutral" }: { text: string; tone?: "neutral" | "success" | "error" }) {
  const styles =
    tone === "success"
      ? "bg-emerald-50 text-emerald-700"
      : tone === "error"
        ? "bg-rose-50 text-rose-700"
        : "bg-slate-100 text-slate-600";
  return <p className={`rounded-2xl px-4 py-3 text-sm ${styles}`}>{text}</p>;
}

function MetricCard({
  title,
  value,
  detail,
  icon: Icon,
}: {
  title: string;
  value: string;
  detail: string;
  icon: typeof Activity;
}) {
  return (
    <div className="panel p-5">
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="eyebrow">{title}</p>
          <h3 className="mt-3 font-display text-3xl text-slate-900">{value}</h3>
          <p className="mt-2 text-sm leading-6 text-slate-500">{detail}</p>
        </div>
        <div className="rounded-2xl bg-[#eef8f8] p-3 text-[#0e7c86]">
          <Icon className="h-5 w-5" />
        </div>
      </div>
    </div>
  );
}

function SectionHeader({
  title,
  description,
  action,
}: {
  title: string;
  description: string;
  action?: ReactNode;
}) {
  return (
    <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
      <div>
        <p className="eyebrow">Aurora workspace</p>
        <h1 className="font-display text-4xl text-slate-900 sm:text-5xl">{title}</h1>
        <p className="mt-3 max-w-3xl text-base leading-7 text-slate-500">{description}</p>
      </div>
      {action}
    </div>
  );
}

function ProgressBars({ history }: { history: ProgressSummary["history"] }) {
  const recent = history.slice(-7);
  if (!recent.length) {
    return <EmptyState title="No progress chart yet" text="Add a few progress logs to see energy and adherence trends here." />;
  }

  return (
    <div className="space-y-4">
      {recent.map((entry) => (
        <div key={`${entry.date}-${entry.mood}`} className="space-y-2">
          <div className="flex items-center justify-between text-sm text-slate-500">
            <span>{formatDate(entry.date)}</span>
            <span>{entry.energy_level}/10 energy</span>
          </div>
          <div className="h-3 overflow-hidden rounded-full bg-slate-100">
            <div className="h-full rounded-full bg-[linear-gradient(90deg,#0e7c86,#72d6b0)]" style={{ width: `${entry.energy_level * 10}%` }} />
          </div>
          <div className="h-2 overflow-hidden rounded-full bg-slate-100">
            <div className="h-full rounded-full bg-[linear-gradient(90deg,#ff9468,#ffc16b)]" style={{ width: `${entry.adherence_score * 10}%` }} />
          </div>
        </div>
      ))}
    </div>
  );
}

function AuthScreen({
  mode,
  onModeChange,
  onSubmit,
  busy,
  error,
}: {
  mode: "login" | "register";
  onModeChange: (mode: "login" | "register") => void;
  onSubmit: (payload: Record<string, string>) => Promise<void>;
  busy: boolean;
  error: string;
}) {
  const [form, setForm] = useState({ name: "", username: "", email: "", password: "" });

  return (
    <main className="min-h-screen px-4 py-6 sm:px-6 lg:px-10">
      <div className="mx-auto grid min-h-[calc(100vh-3rem)] max-w-7xl gap-6 lg:grid-cols-[1.1fr,0.9fr]">
        <section className="relative overflow-hidden rounded-[36px] border border-white/50 bg-[linear-gradient(160deg,rgba(13,42,55,0.94),rgba(6,18,28,0.95))] p-8 text-white shadow-[0_40px_120px_rgba(3,16,24,0.34)] lg:p-12">
          <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_left,rgba(86,232,193,0.22),transparent_32%),radial-gradient(circle_at_bottom_right,rgba(255,135,96,0.2),transparent_28%)]" />
          <div className="relative flex h-full flex-col justify-between gap-10">
            <div className="space-y-6">
              <div className="flex items-center gap-4">
                <div className="flex h-14 w-14 items-center justify-center rounded-3xl bg-white/12 ring-1 ring-white/25">
                  <Sparkles className="h-7 w-7 text-[#8ff0cf]" />
                </div>
                <div>
                  <p className="text-xs font-semibold uppercase tracking-[0.32em] text-[#b9e9dc]">Aurora Health</p>
                  <h1 className="font-display text-3xl sm:text-4xl">A health workspace people can actually use.</h1>
                </div>
              </div>
              <p className="max-w-2xl text-base leading-7 text-white/78 sm:text-lg">
                One clean flow for onboarding, fitness planning, cycle-aware guidance, daily tracking, progress reviews,
                weekly reports, and coach conversations.
              </p>
            </div>
            <div className="grid gap-4 sm:grid-cols-3">
              {[
                { icon: LayoutDashboard, title: "Live dashboard", text: "Workspace, summary, trends, and next actions from the moment a user signs in." },
                { icon: HeartPulse, title: "Women-first care", text: "Cycle logging, symptom patterns, pregnancy and postpartum-aware planning." },
                { icon: Brain, title: "Memory-backed coach", text: "Aurora recalls logs and habits so guidance gets better as the app gets used." },
              ].map(({ icon: Icon, title, text }) => (
                <div key={title} className="rounded-[28px] border border-white/14 bg-white/8 p-5 backdrop-blur">
                  <Icon className="h-5 w-5 text-[#8ff0cf]" />
                  <h2 className="mt-4 font-display text-xl">{title}</h2>
                  <p className="mt-2 text-sm leading-6 text-white/68">{text}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        <section className="flex items-center">
          <div className="panel mx-auto w-full max-w-xl p-6 sm:p-8">
            <div className="mb-8 flex rounded-full bg-[rgba(9,36,48,0.08)] p-1">
              {(["login", "register"] as const).map((item) => (
                <button
                  key={item}
                  type="button"
                  onClick={() => onModeChange(item)}
                  className={`flex-1 rounded-full px-4 py-3 text-sm font-semibold transition ${
                    mode === item ? "bg-[#0e7c86] text-white shadow-[0_12px_30px_rgba(14,124,134,0.28)]" : "text-slate-500"
                  }`}
                >
                  {item === "login" ? "Login" : "Register"}
                </button>
              ))}
            </div>

            <div className="space-y-2">
              <p className="eyebrow">{mode === "login" ? "Welcome back" : "Create your account"}</p>
              <h2 className="font-display text-3xl text-slate-900">
                {mode === "login" ? "Continue into your Aurora workspace." : "Start with your account, then complete your profile."}
              </h2>
            </div>

            <form
              className="mt-8 space-y-4"
              onSubmit={async (event) => {
                event.preventDefault();
                await onSubmit(form);
              }}
            >
              {mode === "register" ? (
                <div className="grid gap-4 sm:grid-cols-2">
                  <label className="field-group">
                    <span>Name</span>
                    <input className="field" value={form.name} onChange={(event) => setForm((current) => ({ ...current, name: event.target.value }))} placeholder="Aarav Sharma" required />
                  </label>
                  <label className="field-group">
                    <span>Username</span>
                    <input className="field" value={form.username} onChange={(event) => setForm((current) => ({ ...current, username: event.target.value }))} placeholder="aaravfit" required />
                  </label>
                </div>
              ) : null}

              <label className="field-group">
                <span>Email</span>
                <input type="email" className="field" value={form.email} onChange={(event) => setForm((current) => ({ ...current, email: event.target.value }))} placeholder="you@example.com" required />
              </label>
              <label className="field-group">
                <span>Password</span>
                <input type="password" className="field" value={form.password} onChange={(event) => setForm((current) => ({ ...current, password: event.target.value }))} placeholder="Minimum 8 characters" required />
              </label>

              {error ? <p className="rounded-2xl bg-rose-50 px-4 py-3 text-sm text-rose-700">{error}</p> : null}

              <button type="submit" className="button-primary w-full justify-center" disabled={busy}>
                {busy ? <LoaderCircle className="h-4 w-4 animate-spin" /> : null}
                {mode === "login" ? "Login to Aurora" : "Create account"}
              </button>
            </form>
          </div>
        </section>
      </div>
    </main>
  );
}

function AppFrame({
  session,
  currentSection,
  onLogout,
  children,
}: {
  session: AuroraSession;
  currentSection: SectionKey;
  onLogout: () => void;
  children: ReactNode;
}) {
  return (
    <div className="mx-auto flex min-h-screen max-w-[1600px] gap-6 px-4 py-4 sm:px-6 lg:px-8">
      <aside className="hidden w-[290px] shrink-0 xl:block">
        <div className="sticky top-4 flex h-[calc(100vh-2rem)] flex-col rounded-[32px] border border-white/70 bg-[rgba(250,251,248,0.88)] p-5 shadow-[0_30px_80px_rgba(10,26,35,0.12)] backdrop-blur">
          <div className="mb-6 flex items-center gap-4">
            <div className="flex h-14 w-14 items-center justify-center rounded-3xl bg-[linear-gradient(135deg,#0e7c86,#72d6b0)] text-white shadow-[0_20px_50px_rgba(14,124,134,0.25)]">
              <Sparkles className="h-6 w-6" />
            </div>
            <div>
              <p className="eyebrow">Aurora Health</p>
              <p className="font-display text-2xl text-slate-900">Fitness OS</p>
            </div>
          </div>

          <div className="rounded-[26px] bg-[linear-gradient(135deg,#0d3340,#174d58)] p-4 text-white">
            <p className="text-sm text-white/72">Logged in as</p>
            <h2 className="mt-1 font-display text-2xl">{session.name}</h2>
            <p className="text-sm text-white/72">{session.email}</p>
          </div>

          <nav className="mt-6 flex-1 space-y-2 overflow-y-auto pr-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              const active = item.key === currentSection || (currentSection === "home" && item.key === "home");
              return (
                <Link
                  key={item.key}
                  href={item.href}
                  className={`block rounded-[24px] border px-4 py-4 transition ${
                    active ? "border-[#0e7c86]/20 bg-[#eefbf7] shadow-[0_18px_40px_rgba(14,124,134,0.08)]" : "border-transparent bg-transparent hover:border-slate-200 hover:bg-white/70"
                  }`}
                >
                  <div className="flex items-start gap-3">
                    <div className={`mt-1 rounded-2xl p-2 ${active ? "bg-[#0e7c86] text-white" : "bg-slate-100 text-slate-500"}`}>
                      <Icon className="h-4 w-4" />
                    </div>
                    <div>
                      <p className="font-semibold text-slate-900">{item.label}</p>
                      <p className="mt-1 text-sm leading-6 text-slate-500">{item.description}</p>
                    </div>
                  </div>
                </Link>
              );
            })}
          </nav>

          <button type="button" className="button-secondary mt-5 justify-center" onClick={onLogout}>
            <LogOut className="h-4 w-4" />
            Logout
          </button>
        </div>
      </aside>
      <div className="min-w-0 flex-1">{children}</div>
    </div>
  );
}

function HomeSection({
  profile,
  data,
  onOpenSection,
}: {
  profile: UserProfile;
  data: DashboardBundle;
  onOpenSection: (section: SectionKey) => void;
}) {
  const completion = useMemo(() => {
    let score = 40;
    if (data.progress.entries > 0) score += 15;
    if (data.history.workout_logs.length > 0) score += 15;
    if (data.history.diet_logs.length > 0) score += 10;
    if (data.history.period_logs.length > 0 || profile.gender.toLowerCase() !== "female") score += 10;
    if (data.history.recent_memories.length > 0) score += 10;
    return Math.min(score, 100);
  }, [data, profile.gender]);

  return (
    <div className="space-y-6">
      <SectionHeader title={`Welcome back, ${profile.name.split(" ")[0] || "there"}`} description="Your home dashboard surfaces today's workspace, weekly summary, progress direction, and every module in one place." />

      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <MetricCard title="Current streak" value={`${data.streak.current_streak} days`} detail={data.streak.motivation} icon={ShieldPlus} />
        <MetricCard title="Progress entries" value={`${data.progress.entries}`} detail={`Trend: ${scoreLabel(data.progress.trend)}`} icon={TrendingUp} />
        <MetricCard title="Next period" value={data.womenHealth.next_period_start ? formatDate(data.womenHealth.next_period_start) : "Track first"} detail={`Phase: ${scoreLabel(data.womenHealth.predicted_phase)}`} icon={HeartPulse} />
        <MetricCard title="Workspace completion" value={`${completion}%`} detail="Higher coverage means better plans, reports, and coaching." icon={Sparkles} />
      </section>

      <section className="grid gap-6 xl:grid-cols-[1.2fr,0.8fr]">
        <div className="panel p-6">
          <div className="flex items-center justify-between gap-4">
            <div>
              <p className="eyebrow">Live workspace</p>
              <h2 className="font-display text-3xl text-slate-900">Today's operating board</h2>
            </div>
            <button type="button" className="button-secondary" onClick={() => onOpenSection("tracking")}>
              Open tracking
              <ArrowRight className="h-4 w-4" />
            </button>
          </div>

          <div className="mt-6 grid gap-4 md:grid-cols-2">
            {[
              { title: "Workout focus", text: data.weeklyReport.recommendations[0] ?? "Generate a plan or log a workout to get a targeted recommendation.", icon: Dumbbell, section: "plans" as SectionKey },
              { title: "Nutrition focus", text: data.womenHealth.nutrition_focus[0] ?? "Hydration, protein, and regular meals stay foundational.", icon: Salad, section: "women-health" as SectionKey },
              { title: "Recovery focus", text: `Sleep ${profile.lifestyle.sleep_hours}h, water ${profile.lifestyle.water_liters}L, stress ${profile.lifestyle.stress_level}/10.`, icon: MoonStar, section: "profile" as SectionKey },
              { title: "Coach focus", text: data.weeklyReport.summary, icon: MessageSquareText, section: "coach" as SectionKey },
            ].map(({ icon: Icon, title, text, section }) => (
              <button key={title} type="button" onClick={() => onOpenSection(section)} className="rounded-[26px] border border-slate-200 bg-slate-50 p-5 text-left transition hover:-translate-y-0.5 hover:bg-white">
                <div className="flex items-center gap-3">
                  <div className="rounded-2xl bg-white p-3 text-[#0e7c86] shadow-sm"><Icon className="h-5 w-5" /></div>
                  <p className="font-semibold text-slate-900">{title}</p>
                </div>
                <p className="mt-4 text-sm leading-6 text-slate-500">{compactText(text)}</p>
              </button>
            ))}
          </div>
        </div>

        <div className="panel p-6">
          <p className="eyebrow">Weekly summary</p>
          <h2 className="mt-2 font-display text-3xl text-slate-900">Aurora snapshot</h2>
          <p className="mt-4 text-sm leading-7 text-slate-500">{data.weeklyReport.summary}</p>
          <div className="mt-6 grid gap-4">
            <div className="rounded-[24px] bg-[#f8faf9] p-4">
              <p className="font-semibold text-slate-900">Wins</p>
              <ul className="mt-3 space-y-2 text-sm leading-6 text-slate-500">
                {(data.weeklyReport.wins.length ? data.weeklyReport.wins : ["Start logging activity to generate visible wins."]).map((item) => <li key={item}>- {item}</li>)}
              </ul>
            </div>
            <div className="rounded-[24px] bg-[#fff8f3] p-4">
              <p className="font-semibold text-slate-900">Watchouts</p>
              <ul className="mt-3 space-y-2 text-sm leading-6 text-slate-500">
                {(data.weeklyReport.risks.length ? data.weeklyReport.risks : ["No major risks surfaced yet."]).map((item) => <li key={item}>- {item}</li>)}
              </ul>
            </div>
          </div>
        </div>
      </section>

      <section className="grid gap-6 xl:grid-cols-[0.9fr,1.1fr]">
        <div className="panel p-6">
          <p className="eyebrow">Progress graph</p>
          <h2 className="mt-2 font-display text-3xl text-slate-900">Energy and adherence</h2>
          <div className="mt-6"><ProgressBars history={data.progress.history} /></div>
        </div>

        <div className="panel p-6">
          <p className="eyebrow">Modules</p>
          <h2 className="mt-2 font-display text-3xl text-slate-900">Everything in one system</h2>
          <div className="mt-6 grid gap-4 md:grid-cols-2">
            {navItems.slice(1).map((item) => {
              const Icon = item.icon;
              return (
                <button key={item.key} type="button" onClick={() => onOpenSection(item.key)} className="rounded-[24px] border border-slate-200 bg-white p-5 text-left transition hover:-translate-y-0.5 hover:shadow-[0_20px_50px_rgba(10,26,35,0.08)]">
                  <div className="flex items-center gap-3">
                    <div className="rounded-2xl bg-[#eef8f8] p-3 text-[#0e7c86]"><Icon className="h-5 w-5" /></div>
                    <p className="font-semibold text-slate-900">{item.label}</p>
                  </div>
                  <p className="mt-4 text-sm leading-6 text-slate-500">{item.description}</p>
                </button>
              );
            })}
          </div>
        </div>
      </section>
    </div>
  );
}

function ProfileSection({
  draft,
  setDraft,
  saving,
  submitLabel,
  status,
  onSave,
}: {
  draft: UserProfile;
  setDraft: Dispatch<SetStateAction<UserProfile>>;
  saving: boolean;
  submitLabel: string;
  status: string;
  onSave: () => Promise<void>;
}) {
  return (
    <div className="space-y-6">
      <SectionHeader title="Profile setup" description="Make this easy to complete: demographics, goals, lifestyle, women-specific context, and food preferences all feed the plan engine and coach." />
      <div className="panel p-6">
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          <label className="field-group"><span>Name</span><input className="field" value={draft.name} onChange={(e) => setDraft((c) => ({ ...c, name: e.target.value }))} /></label>
          <label className="field-group"><span>Age</span><input type="number" className="field" value={draft.age} onChange={(e) => setDraft((c) => ({ ...c, age: Number(e.target.value) }))} /></label>
          <label className="field-group"><span>Gender</span><select className="field" value={draft.gender} onChange={(e) => setDraft((c) => ({ ...c, gender: e.target.value }))}><option value="female">Female</option><option value="male">Male</option><option value="non-binary">Non-binary</option></select></label>
          <label className="field-group"><span>Weight (kg)</span><input type="number" className="field" value={draft.weight} onChange={(e) => setDraft((c) => ({ ...c, weight: Number(e.target.value) }))} /></label>
          <label className="field-group"><span>Height (cm)</span><input type="number" className="field" value={draft.height_cm} onChange={(e) => setDraft((c) => ({ ...c, height_cm: Number(e.target.value) }))} /></label>
          <label className="field-group"><span>Fitness level</span><select className="field" value={draft.level} onChange={(e) => setDraft((c) => ({ ...c, level: e.target.value }))}><option value="beginner">Beginner</option><option value="intermediate">Intermediate</option><option value="advanced">Advanced</option></select></label>
        </div>

        <div className="mt-5 grid gap-4 md:grid-cols-2">
          <label className="field-group"><span>Main goal</span><input className="field" value={draft.goal} onChange={(e) => setDraft((c) => ({ ...c, goal: e.target.value }))} /></label>
          <label className="field-group"><span>Activity level</span><select className="field" value={draft.lifestyle.activity_level} onChange={(e) => setDraft((c) => ({ ...c, lifestyle: { ...c.lifestyle, activity_level: e.target.value } }))}><option value="sedentary">Sedentary</option><option value="light">Light</option><option value="moderate">Moderate</option><option value="high">High</option></select></label>
        </div>

        <div className="mt-5 grid gap-4 md:grid-cols-3">
          <label className="field-group"><span>Sleep hours</span><input type="number" step="0.5" className="field" value={draft.lifestyle.sleep_hours} onChange={(e) => setDraft((c) => ({ ...c, lifestyle: { ...c.lifestyle, sleep_hours: Number(e.target.value) } }))} /></label>
          <label className="field-group"><span>Water liters</span><input type="number" step="0.1" className="field" value={draft.lifestyle.water_liters} onChange={(e) => setDraft((c) => ({ ...c, lifestyle: { ...c.lifestyle, water_liters: Number(e.target.value) } }))} /></label>
          <label className="field-group"><span>Stress level</span><input type="number" min="1" max="10" className="field" value={draft.lifestyle.stress_level} onChange={(e) => setDraft((c) => ({ ...c, lifestyle: { ...c.lifestyle, stress_level: Number(e.target.value) } }))} /></label>
        </div>

        <div className="mt-5 grid gap-4 md:grid-cols-2">
          <label className="field-group"><span>Dietary preference</span><input className="field" value={draft.lifestyle.dietary_preference} onChange={(e) => setDraft((c) => ({ ...c, lifestyle: { ...c.lifestyle, dietary_preference: e.target.value } }))} placeholder="Balanced, vegetarian, high-protein" /></label>
          <label className="field-group"><span>Health goals</span><input className="field" value={listToText(draft.lifestyle.health_goals)} onChange={(e) => setDraft((c) => ({ ...c, lifestyle: { ...c.lifestyle, health_goals: parseList(e.target.value) } }))} placeholder="better energy, weight loss, stronger legs" /></label>
          <label className="field-group"><span>Hormonal concerns</span><input className="field" value={listToText(draft.hormonal_concerns)} onChange={(e) => setDraft((c) => ({ ...c, hormonal_concerns: parseList(e.target.value) }))} placeholder="pcos, acne, mood swings" /></label>
          <label className="field-group"><span>Dietary restrictions</span><input className="field" value={listToText(draft.dietary_restrictions)} onChange={(e) => setDraft((c) => ({ ...c, dietary_restrictions: parseList(e.target.value) }))} placeholder="lactose, gluten, no eggs" /></label>
        </div>

        <div className="mt-5 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          <label className="toggle"><input type="checkbox" checked={draft.pregnant} onChange={(e) => setDraft((c) => ({ ...c, pregnant: e.target.checked }))} /><span>Pregnant</span></label>
          <label className="toggle"><input type="checkbox" checked={draft.postpartum} onChange={(e) => setDraft((c) => ({ ...c, postpartum: e.target.checked }))} /><span>Postpartum</span></label>
          <label className="field-group"><span>Pregnancy trimester</span><input type="number" min="1" max="3" className="field" value={draft.pregnancy_trimester ?? ""} onChange={(e) => setDraft((c) => ({ ...c, pregnancy_trimester: e.target.value ? Number(e.target.value) : null }))} /></label>
          <label className="field-group"><span>Postpartum weeks</span><input type="number" min="0" className="field" value={draft.postpartum_weeks ?? ""} onChange={(e) => setDraft((c) => ({ ...c, postpartum_weeks: e.target.value ? Number(e.target.value) : null }))} /></label>
        </div>

        <div className="mt-6 flex flex-col gap-3 sm:flex-row sm:items-center">
          <button type="button" className="button-primary" disabled={saving} onClick={onSave}>{saving ? <LoaderCircle className="h-4 w-4 animate-spin" /> : null}{submitLabel}</button>
          {status ? <StatusNotice text={status} tone={status.toLowerCase().includes("saved") ? "success" : "neutral"} /> : null}
        </div>
      </div>
    </div>
  );
}

function PlansSection({ profile, womenHealth, plan, generating, planStatus, onGenerate }: { profile: UserProfile; womenHealth: WomenHealthDashboard; plan: PlanResponse | null; generating: boolean; planStatus: string; onGenerate: () => Promise<void>; }) {
  return (
    <div className="space-y-6">
      <SectionHeader title="Plans" description="Generate a practical workout, food, and women-aware guidance from the saved profile instead of showing fake modules." action={<button type="button" className="button-primary" disabled={generating} onClick={onGenerate}>{generating ? <LoaderCircle className="h-4 w-4 animate-spin" /> : null}Generate plan</button>} />
      <div className="grid gap-6 xl:grid-cols-[0.8fr,1.2fr]">
        <div className="panel p-6">
          <p className="eyebrow">Inputs Aurora will use</p>
          <div className="mt-4 space-y-3 text-sm leading-6 text-slate-600">
            <p><strong>Goal:</strong> {profile.goal}</p>
            <p><strong>Level:</strong> {profile.level}</p>
            <p><strong>Activity level:</strong> {profile.lifestyle.activity_level}</p>
            <p><strong>Diet preference:</strong> {profile.lifestyle.dietary_preference}</p>
            <p><strong>Cycle phase:</strong> {scoreLabel(womenHealth.predicted_phase)}</p>
            <p><strong>Hormonal concerns:</strong> {listToText(profile.hormonal_concerns) || "None"}</p>
          </div>
          {planStatus ? <div className="mt-5"><StatusNotice text={planStatus} tone="neutral" /></div> : null}
        </div>
        <div className="space-y-4">
          <div className="panel p-6"><p className="eyebrow">Workout</p><p className="mt-3 whitespace-pre-wrap text-sm leading-7 text-slate-600">{compactText(plan?.workout ?? "Generate a plan to fill this with a workout program.")}</p></div>
          <div className="panel p-6"><p className="eyebrow">Diet</p><p className="mt-3 whitespace-pre-wrap text-sm leading-7 text-slate-600">{compactText(plan?.diet ?? "Diet guidance will appear here after plan generation.")}</p></div>
          <div className="panel p-6"><p className="eyebrow">Women's health guidance</p><p className="mt-3 whitespace-pre-wrap text-sm leading-7 text-slate-600">{compactText(plan?.women_health ?? "If relevant to the profile, Aurora will add cycle, pregnancy, or postpartum-aware guidance here.")}</p></div>
        </div>
      </div>
    </div>
  );
}

function ReportsSection({ report }: { report: WeeklyReport }) {
  return (
    <div className="space-y-6">
      <SectionHeader title="Weekly report" description="This module turns your logs into a compact weekly review with wins, risks, and recommendations that feel actionable." />
      <div className="grid gap-6 xl:grid-cols-[0.95fr,1.05fr]">
        <div className="panel p-6">
          <p className="eyebrow">Summary</p>
          <h2 className="mt-2 font-display text-3xl text-slate-900">{report.period_start && report.period_end ? `${formatDate(report.period_start)} to ${formatDate(report.period_end)}` : "Current week"}</h2>
          <p className="mt-4 text-sm leading-7 text-slate-600">{report.summary}</p>
        </div>
        <div className="grid gap-4">
          <div className="panel p-6"><p className="eyebrow">Wins</p><ul className="mt-4 space-y-3 text-sm leading-6 text-slate-600">{(report.wins.length ? report.wins : ["Add more logs this week to surface wins."]).map((item) => <li key={item}>- {item}</li>)}</ul></div>
          <div className="panel p-6"><p className="eyebrow">Risks</p><ul className="mt-4 space-y-3 text-sm leading-6 text-slate-600">{(report.risks.length ? report.risks : ["No major risk flags yet."]).map((item) => <li key={item}>- {item}</li>)}</ul></div>
          <div className="panel p-6"><p className="eyebrow">Recommendations</p><ul className="mt-4 space-y-3 text-sm leading-6 text-slate-600">{(report.recommendations.length ? report.recommendations : ["Recommendations will appear as your data grows."]).map((item) => <li key={item}>- {item}</li>)}</ul></div>
        </div>
      </div>
    </div>
  );
}

function TrackingSection({ history, workoutForm, setWorkoutForm, dietForm, setDietForm, feedbackForm, setFeedbackForm, checkinForm, setCheckinForm, trackingStatus, submitting, onSubmitWorkout, onSubmitDiet, onSubmitFeedback, onSubmitCheckin }: {
  history: HistoryResponse;
  workoutForm: WorkoutFormState;
  setWorkoutForm: Dispatch<SetStateAction<WorkoutFormState>>;
  dietForm: DietFormState;
  setDietForm: Dispatch<SetStateAction<DietFormState>>;
  feedbackForm: FeedbackFormState;
  setFeedbackForm: Dispatch<SetStateAction<FeedbackFormState>>;
  checkinForm: CheckinFormState;
  setCheckinForm: Dispatch<SetStateAction<CheckinFormState>>;
  trackingStatus: string;
  submitting: boolean;
  onSubmitWorkout: () => Promise<void>;
  onSubmitDiet: () => Promise<void>;
  onSubmitFeedback: () => Promise<void>;
  onSubmitCheckin: () => Promise<void>;
}) {
  return (
    <div className="space-y-6">
      <SectionHeader title="Daily tracking" description="Fast forms, low friction, and the same kind of easy entry flow the Streamlit app had, but in a usable product layout." />
      {trackingStatus ? <StatusNotice text={trackingStatus} tone="success" /> : null}
      <div className="grid gap-6 xl:grid-cols-2">
        <div className="panel p-6">
          <p className="eyebrow">Workout log</p>
          <div className="mt-4 grid gap-4 md:grid-cols-2">
            <label className="field-group"><span>Date</span><input type="date" className="field" value={workoutForm.date} onChange={(e) => setWorkoutForm((c) => ({ ...c, date: e.target.value }))} /></label>
            <label className="field-group"><span>Workout type</span><input className="field" value={workoutForm.workout_type} onChange={(e) => setWorkoutForm((c) => ({ ...c, workout_type: e.target.value }))} /></label>
            <label className="field-group"><span>Duration minutes</span><input type="number" className="field" value={workoutForm.duration_minutes} onChange={(e) => setWorkoutForm((c) => ({ ...c, duration_minutes: Number(e.target.value) }))} /></label>
            <label className="field-group"><span>Intensity</span><select className="field" value={workoutForm.intensity} onChange={(e) => setWorkoutForm((c) => ({ ...c, intensity: e.target.value }))}><option value="low">Low</option><option value="moderate">Moderate</option><option value="high">High</option></select></label>
          </div>
          <label className="field-group mt-4"><span>Notes</span><textarea className="field min-h-28 resize-y" value={workoutForm.notes} onChange={(e) => setWorkoutForm((c) => ({ ...c, notes: e.target.value }))} /></label>
          <button type="button" className="button-primary mt-4" disabled={submitting} onClick={onSubmitWorkout}>{submitting ? <LoaderCircle className="h-4 w-4 animate-spin" /> : null}Save workout</button>
        </div>
        <div className="panel p-6">
          <p className="eyebrow">Diet log</p>
          <div className="mt-4 grid gap-4 md:grid-cols-2">
            <label className="field-group"><span>Date</span><input type="date" className="field" value={dietForm.date} onChange={(e) => setDietForm((c) => ({ ...c, date: e.target.value }))} /></label>
            <label className="field-group"><span>Meals followed</span><input type="number" className="field" value={dietForm.meals_followed} onChange={(e) => setDietForm((c) => ({ ...c, meals_followed: Number(e.target.value) }))} /></label>
            <label className="field-group"><span>Hydration liters</span><input type="number" step="0.1" className="field" value={dietForm.hydration_liters} onChange={(e) => setDietForm((c) => ({ ...c, hydration_liters: Number(e.target.value) }))} /></label>
            <label className="field-group"><span>Protein grams</span><input type="number" className="field" value={dietForm.protein_grams ?? ""} onChange={(e) => setDietForm((c) => ({ ...c, protein_grams: e.target.value ? Number(e.target.value) : null }))} /></label>
          </div>
          <label className="field-group mt-4"><span>Cravings</span><input className="field" value={dietForm.cravings} onChange={(e) => setDietForm((c) => ({ ...c, cravings: e.target.value }))} placeholder="salty snacks, sweets" /></label>
          <label className="field-group mt-4"><span>Notes</span><textarea className="field min-h-28 resize-y" value={dietForm.notes} onChange={(e) => setDietForm((c) => ({ ...c, notes: e.target.value }))} /></label>
          <button type="button" className="button-primary mt-4" disabled={submitting} onClick={onSubmitDiet}>{submitting ? <LoaderCircle className="h-4 w-4 animate-spin" /> : null}Save diet</button>
        </div>
      </div>
      <div className="grid gap-6 xl:grid-cols-[0.8fr,1.2fr]">
        <div className="space-y-6">
          <div className="panel p-6">
            <p className="eyebrow">Daily check-in</p>
            <label className="field-group mt-4"><span>Date</span><input type="date" className="field" value={checkinForm.date} onChange={(e) => setCheckinForm((c) => ({ ...c, date: e.target.value }))} /></label>
            <div className="mt-4 grid gap-3">
              <label className="toggle"><input type="checkbox" checked={checkinForm.workout_completed} onChange={(e) => setCheckinForm((c) => ({ ...c, workout_completed: e.target.checked }))} /><span>Workout completed</span></label>
              <label className="toggle"><input type="checkbox" checked={checkinForm.nutrition_completed} onChange={(e) => setCheckinForm((c) => ({ ...c, nutrition_completed: e.target.checked }))} /><span>Nutrition completed</span></label>
            </div>
            <label className="field-group mt-4"><span>Journal note</span><textarea className="field min-h-24 resize-y" value={checkinForm.journal_note} onChange={(e) => setCheckinForm((c) => ({ ...c, journal_note: e.target.value }))} /></label>
            <button type="button" className="button-secondary mt-4" disabled={submitting} onClick={onSubmitCheckin}>Submit check-in</button>
          </div>
          <div className="panel p-6">
            <p className="eyebrow">App feedback</p>
            <label className="field-group mt-4"><span>Category</span><input className="field" value={feedbackForm.category} onChange={(e) => setFeedbackForm((c) => ({ ...c, category: e.target.value }))} /></label>
            <label className="field-group mt-4"><span>Feedback</span><textarea className="field min-h-24 resize-y" value={feedbackForm.feedback} onChange={(e) => setFeedbackForm((c) => ({ ...c, feedback: e.target.value }))} /></label>
            <label className="field-group mt-4"><span>Rating</span><input type="number" min="1" max="10" className="field" value={feedbackForm.rating ?? ""} onChange={(e) => setFeedbackForm((c) => ({ ...c, rating: e.target.value ? Number(e.target.value) : null }))} /></label>
            <button type="button" className="button-secondary mt-4" disabled={submitting} onClick={onSubmitFeedback}>Save feedback</button>
          </div>
        </div>
        <div className="panel p-6">
          <p className="eyebrow">Recent history</p>
          <div className="mt-5 grid gap-4 md:grid-cols-2">
            <div className="rounded-[24px] bg-slate-50 p-4">
              <p className="font-semibold text-slate-900">Workouts</p>
              <div className="mt-3 space-y-3">
                {history.workout_logs.slice(0, 4).map((item) => <div key={`${item.date}-${item.workout_type}`} className="rounded-2xl bg-white p-3"><p className="font-medium text-slate-900">{item.workout_type}</p><p className="text-sm text-slate-500">{formatDate(item.date)} | {item.duration_minutes} min | {item.intensity}</p></div>)}
                {!history.workout_logs.length ? <EmptyState title="No workout logs" text="Use the form to add your first workout." /> : null}
              </div>
            </div>
            <div className="rounded-[24px] bg-slate-50 p-4">
              <p className="font-semibold text-slate-900">Diet</p>
              <div className="mt-3 space-y-3">
                {history.diet_logs.slice(0, 4).map((item) => <div key={`${item.date}-${item.meals_followed}`} className="rounded-2xl bg-white p-3"><p className="font-medium text-slate-900">{item.meals_followed} meals followed</p><p className="text-sm text-slate-500">{formatDate(item.date)} | {item.hydration_liters}L hydration</p></div>)}
                {!history.diet_logs.length ? <EmptyState title="No diet logs" text="Add nutrition tracking to improve diet guidance." /> : null}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function ProgressSection({ progress, form, setForm, progressStatus, submitting, onSubmit }: {
  progress: ProgressSummary;
  form: ProgressFormState;
  setForm: Dispatch<SetStateAction<ProgressFormState>>;
  progressStatus: string;
  submitting: boolean;
  onSubmit: () => Promise<void>;
}) {
  return (
    <div className="space-y-6">
      <SectionHeader title="Progress" description="Track weight, mood, workout time, adherence, and energy so the app can show real momentum instead of empty graphs." />
      <div className="grid gap-6 xl:grid-cols-[0.9fr,1.1fr]">
        <div className="panel p-6">
          <p className="eyebrow">Progress log</p>
          <div className="mt-4 grid gap-4 md:grid-cols-2">
            <label className="field-group"><span>Date</span><input type="date" className="field" value={form.date} onChange={(e) => setForm((c) => ({ ...c, date: e.target.value }))} /></label>
            <label className="field-group"><span>Weight (kg)</span><input type="number" step="0.1" className="field" value={form.weight ?? ""} onChange={(e) => setForm((c) => ({ ...c, weight: e.target.value ? Number(e.target.value) : null }))} /></label>
            <label className="field-group"><span>Energy level</span><input type="number" min="1" max="10" className="field" value={form.energy_level} onChange={(e) => setForm((c) => ({ ...c, energy_level: Number(e.target.value) }))} /></label>
            <label className="field-group"><span>Mood</span><input className="field" value={form.mood} onChange={(e) => setForm((c) => ({ ...c, mood: e.target.value }))} /></label>
            <label className="field-group"><span>Workout minutes</span><input type="number" className="field" value={form.workout_minutes} onChange={(e) => setForm((c) => ({ ...c, workout_minutes: Number(e.target.value) }))} /></label>
            <label className="field-group"><span>Adherence score</span><input type="number" min="1" max="10" className="field" value={form.adherence_score} onChange={(e) => setForm((c) => ({ ...c, adherence_score: Number(e.target.value) }))} /></label>
          </div>
          <label className="field-group mt-4"><span>Notes</span><textarea className="field min-h-28 resize-y" value={form.notes} onChange={(e) => setForm((c) => ({ ...c, notes: e.target.value }))} /></label>
          <div className="mt-4 flex flex-col gap-3 sm:flex-row sm:items-center">
            <button type="button" className="button-primary" disabled={submitting} onClick={onSubmit}>{submitting ? <LoaderCircle className="h-4 w-4 animate-spin" /> : null}Save progress</button>
            {progressStatus ? <StatusNotice text={progressStatus} tone="success" /> : null}
          </div>
        </div>
        <div className="space-y-6">
          <div className="panel p-6"><p className="eyebrow">Current summary</p><div className="mt-4 grid gap-4 md:grid-cols-3"><MetricCard title="Entries" value={`${progress.entries}`} detail="Total progress logs saved" icon={TrendingUp} /><MetricCard title="Trend" value={scoreLabel(progress.trend)} detail="Compared against your earliest entry" icon={Sparkles} /><MetricCard title="Latest workout" value={`${progress.latest?.workout_minutes ?? 0} min`} detail={progress.latest?.mood ?? "No latest entry"} icon={Dumbbell} /></div></div>
          <div className="panel p-6"><p className="eyebrow">Trend chart</p><div className="mt-5"><ProgressBars history={progress.history} /></div></div>
        </div>
      </div>
    </div>
  );
}

function WomenHealthSection({ womenHealth, periodForm, setPeriodForm, periodStatus, submitting, onSubmit }: {
  womenHealth: WomenHealthDashboard;
  periodForm: PeriodFormState;
  setPeriodForm: Dispatch<SetStateAction<PeriodFormState>>;
  periodStatus: string;
  submitting: boolean;
  onSubmit: () => Promise<void>;
}) {
  return (
    <div className="space-y-6">
      <SectionHeader title="Women's health" description="Cycle-aware tracking, symptom logging, nutrition focus, and workout adjustments in a clear dashboard instead of hidden forms." />
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <MetricCard title="Current phase" value={scoreLabel(womenHealth.predicted_phase)} detail="Aurora's cycle phase estimate" icon={HeartPulse} />
        <MetricCard title="Cycle length" value={formatNumber(womenHealth.average_cycle_length, " days")} detail="Average cycle length" icon={CalendarRange} />
        <MetricCard title="Period length" value={formatNumber(womenHealth.average_period_length, " days")} detail="Average bleed duration" icon={ShieldPlus} />
        <MetricCard title="Irregularity" value={scoreLabel(womenHealth.irregularity_score)} detail="Pattern stability based on logs" icon={Sparkles} />
      </div>
      <div className="grid gap-6 xl:grid-cols-[0.85fr,1.15fr]">
        <div className="panel p-6">
          <p className="eyebrow">Log period</p>
          <div className="mt-4 grid gap-4 md:grid-cols-2">
            <label className="field-group"><span>Start date</span><input type="date" className="field" value={periodForm.start_date} onChange={(e) => setPeriodForm((c) => ({ ...c, start_date: e.target.value }))} /></label>
            <label className="field-group"><span>End date</span><input type="date" className="field" value={periodForm.end_date} onChange={(e) => setPeriodForm((c) => ({ ...c, end_date: e.target.value }))} /></label>
            <label className="field-group"><span>Flow level</span><select className="field" value={periodForm.flow_level} onChange={(e) => setPeriodForm((c) => ({ ...c, flow_level: e.target.value }))}><option value="light">Light</option><option value="moderate">Moderate</option><option value="heavy">Heavy</option></select></label>
            <label className="field-group"><span>Mood</span><input className="field" value={periodForm.mood} onChange={(e) => setPeriodForm((c) => ({ ...c, mood: e.target.value }))} /></label>
          </div>
          <label className="field-group mt-4"><span>Symptoms</span><input className="field" value={periodForm.symptoms} onChange={(e) => setPeriodForm((c) => ({ ...c, symptoms: e.target.value }))} placeholder="cramps, fatigue, acne" /></label>
          <label className="field-group mt-4"><span>Cravings</span><input className="field" value={periodForm.cravings} onChange={(e) => setPeriodForm((c) => ({ ...c, cravings: e.target.value }))} /></label>
          <label className="field-group mt-4"><span>Notes</span><textarea className="field min-h-24 resize-y" value={periodForm.notes} onChange={(e) => setPeriodForm((c) => ({ ...c, notes: e.target.value }))} /></label>
          <div className="mt-4 flex flex-col gap-3 sm:flex-row sm:items-center">
            <button type="button" className="button-primary" disabled={submitting} onClick={onSubmit}>{submitting ? <LoaderCircle className="h-4 w-4 animate-spin" /> : null}Save period log</button>
            {periodStatus ? <StatusNotice text={periodStatus} tone="success" /> : null}
          </div>
        </div>
        <div className="space-y-6">
          <div className="panel p-6"><p className="eyebrow">Nutrition focus</p><ul className="mt-4 space-y-3 text-sm leading-6 text-slate-600">{(womenHealth.nutrition_focus.length ? womenHealth.nutrition_focus : ["Add a few logs to personalize this area."]).map((item) => <li key={item}>- {item}</li>)}</ul></div>
          <div className="panel p-6"><p className="eyebrow">Workout focus</p><ul className="mt-4 space-y-3 text-sm leading-6 text-slate-600">{(womenHealth.workout_focus.length ? womenHealth.workout_focus : ["No workout focus yet."]).map((item) => <li key={item}>- {item}</li>)}</ul></div>
          <div className="panel p-6"><p className="eyebrow">Possible concerns</p><ul className="mt-4 space-y-3 text-sm leading-6 text-slate-600">{(womenHealth.possible_concerns.length ? womenHealth.possible_concerns.map((item) => `${item.flag}: ${item.detail}`) : [womenHealth.disclaimer]).map((item) => <li key={item}>- {item}</li>)}</ul></div>
        </div>
      </div>
    </div>
  );
}

function MemorySection({ history, memoryQuery, setMemoryQuery, memoryResults, memoryLoading }: { history: HistoryResponse; memoryQuery: string; setMemoryQuery: (value: string) => void; memoryResults: Array<Record<string, unknown>>; memoryLoading: boolean; }) {
  return (
    <div className="space-y-6">
      <SectionHeader title="Memory and history" description="All logs create usable memory. Search what Aurora remembers, and inspect workout, diet, progress, and period history in one place." />
      <div className="panel p-6">
        <p className="eyebrow">Memory search</p>
        <div className="mt-4 flex flex-col gap-3 sm:flex-row">
          <input className="field flex-1" value={memoryQuery} onChange={(e) => setMemoryQuery(e.target.value)} placeholder="Search for sleep, cravings, fatigue, mood, consistency..." />
          <div className="flex items-center rounded-2xl bg-slate-100 px-4 text-sm text-slate-500">{memoryLoading ? "Searching..." : `${memoryResults.length} results`}</div>
        </div>
        <div className="mt-5 grid gap-3">
          {memoryResults.map((item, index) => <div key={`${String(item.content)}-${index}`} className="rounded-[24px] bg-slate-50 p-4"><p className="font-semibold text-slate-900">{String(item.memory_type ?? "memory")}</p><p className="mt-2 text-sm leading-6 text-slate-600">{String(item.content ?? "")}</p></div>)}
          {!memoryLoading && !memoryResults.length ? <EmptyState title="No memory results" text="Try searching for symptoms, workouts, mood, recovery, or feedback." /> : null}
        </div>
      </div>
      <div className="grid gap-6 xl:grid-cols-2">
        <div className="panel p-6">
          <p className="eyebrow">Recent memories</p>
          <div className="mt-4 space-y-3">
            {history.recent_memories.map((item, index) => <div key={`${item.content}-${index}`} className="rounded-[24px] bg-slate-50 p-4"><p className="font-semibold text-slate-900">{item.memory_type ?? "memory"}</p><p className="mt-2 text-sm leading-6 text-slate-600">{item.content ?? ""}</p><p className="mt-2 text-xs uppercase tracking-[0.18em] text-slate-400">{formatDate(item.created_at)}</p></div>)}
            {!history.recent_memories.length ? <EmptyState title="No memories yet" text="Logging activity automatically populates this section." /> : null}
          </div>
        </div>
        <div className="panel p-6">
          <p className="eyebrow">History digest</p>
          <div className="mt-4 space-y-4">
            {[
              ["Workout logs", history.workout_logs.length],
              ["Diet logs", history.diet_logs.length],
              ["Progress logs", history.progress_logs.length],
              ["Period logs", history.period_logs.length],
            ].map(([label, value]) => <div key={label} className="flex items-center justify-between rounded-[22px] bg-slate-50 px-4 py-4"><span className="font-medium text-slate-900">{label}</span><span className="text-sm text-slate-500">{value} saved</span></div>)}
          </div>
        </div>
      </div>
    </div>
  );
}

function CoachSection({ prompt, setPrompt, response, sending, onSend }: { prompt: string; setPrompt: (value: string) => void; response: CoachResponse | null; sending: boolean; onSend: () => Promise<void>; }) {
  return (
    <div className="space-y-6">
      <SectionHeader title="Aurora coach" description="This is the personalized coach endpoint from the backend. It uses your progress history and profile instead of generic demo copy." />
      <div className="grid gap-6 xl:grid-cols-[0.85fr,1.15fr]">
        <div className="panel p-6">
          <p className="eyebrow">Ask Aurora</p>
          <label className="field-group mt-4"><span>Your question</span><textarea className="field min-h-40 resize-y" value={prompt} onChange={(e) => setPrompt(e.target.value)} placeholder="How should I improve my consistency without overtraining?" /></label>
          <button type="button" className="button-primary mt-4" disabled={sending} onClick={onSend}>{sending ? <LoaderCircle className="h-4 w-4 animate-spin" /> : null}Ask Aurora</button>
        </div>
        <div className="space-y-4">
          <div className="panel p-6"><p className="eyebrow">Reply</p><p className="mt-4 text-sm leading-7 text-slate-600">{compactText(response?.reply ?? "Ask a question to get personalized coaching, insights, and next steps.")}</p></div>
          <div className="panel p-6"><p className="eyebrow">Insights</p><ul className="mt-4 space-y-3 text-sm leading-6 text-slate-600">{(response?.insights?.length ? response.insights : ["Insights will show up here once Aurora responds."]).map((item) => <li key={item}>- {item}</li>)}</ul></div>
          <div className="panel p-6"><p className="eyebrow">Next steps</p><ul className="mt-4 space-y-3 text-sm leading-6 text-slate-600">{(response?.next_steps?.length ? response.next_steps : ["Next steps will appear here after a coach response."]).map((item) => <li key={item}>- {item}</li>)}</ul></div>
        </div>
      </div>
    </div>
  );
}

function AuroraAssistant({ section, session, profile }: { section: SectionKey; session: AuroraSession | null; profile: UserProfile | null; }) {
  const [messages, setMessages] = useState<AssistantMessage[]>([{ role: "assistant", content: "I am Aurora. I can explain each page, suggest the next action, and help users move through the app without guessing." }]);
  const [input, setInput] = useState("");
  const [open, setOpen] = useState(false);
  const [sending, startSending] = useTransition();

  async function sendMessage(message: string) {
    if (!message.trim()) return;
    const userMessage = message.trim();
    setMessages((current) => [...current, { role: "user", content: userMessage }]);
    setInput("");

    startSending(async () => {
      try {
        const reply = await publicBackendRequest<{ reply: string }>("/chat", {
          method: "POST",
          body: JSON.stringify({
            message: [
              "You are Aurora, the in-app guide for a health and fitness product.",
              `Current page: ${section}.`,
              `User logged in: ${session ? "yes" : "no"}.`,
              `Profile goal: ${profile?.goal ?? "not set"}.`,
              `Respond briefly and practically. User message: ${userMessage}`,
            ].join(" "),
          }),
        });
        setMessages((current) => [...current, { role: "assistant", content: reply.reply }]);
      } catch (error) {
        setMessages((current) => [...current, { role: "assistant", content: `I could not reach the guide service. ${normalizeError(error)}` }]);
      }
    });
  }

  return (
    <div className="fixed bottom-4 right-4 z-40 flex flex-col items-end gap-3">
      {open ? (
        <div className="w-[min(420px,calc(100vw-2rem))] overflow-hidden rounded-[32px] border border-[#0e7c86]/14 bg-[rgba(252,255,253,0.94)] shadow-[0_25px_80px_rgba(10,26,35,0.18)] backdrop-blur">
          <div className="flex items-center justify-between gap-4 border-b border-slate-200/80 bg-[linear-gradient(135deg,#0d3340,#174d58)] px-5 py-4 text-white">
            <div className="flex items-center gap-4">
              <div className="flex h-12 w-12 items-center justify-center rounded-3xl bg-white/14 ring-1 ring-white/20"><Sparkles className="h-5 w-5 text-[#a4f0da]" /></div>
              <div><p className="font-display text-2xl">Aurora</p><p className="text-sm text-white/70">Guide, coach, and app navigator</p></div>
            </div>
            <button type="button" aria-label="Close Aurora assistant" className="flex h-10 w-10 items-center justify-center rounded-2xl bg-white/10 text-white transition hover:bg-white/20" onClick={() => setOpen(false)}><X className="h-5 w-5" /></button>
          </div>
          <div className="max-h-[360px] space-y-3 overflow-y-auto px-4 py-4">
            {messages.slice(-5).map((message, index) => <div key={`${message.role}-${index}`} className={`rounded-[24px] px-4 py-3 text-sm leading-6 ${message.role === "assistant" ? "bg-slate-100 text-slate-700" : "ml-10 bg-[#0e7c86] text-white"}`}>{message.content}</div>)}
          </div>
          <div className="border-t border-slate-200/80 px-4 py-4">
            <div className="mb-3 flex flex-wrap gap-2">
              {sectionPrompts[section].map((prompt) => <button key={prompt} type="button" onClick={() => void sendMessage(prompt)} className="chip">{prompt}</button>)}
            </div>
            <div className="flex gap-3">
              <input className="field flex-1" value={input} onChange={(e) => setInput(e.target.value)} placeholder="Ask Aurora how to use this page..." />
              <button type="button" className="button-primary px-4" disabled={sending} onClick={() => void sendMessage(input)}>{sending ? <LoaderCircle className="h-4 w-4 animate-spin" /> : "Send"}</button>
            </div>
          </div>
        </div>
      ) : null}
      <button
        type="button"
        aria-expanded={open}
        aria-label={open ? "Hide Aurora assistant" : "Open Aurora assistant"}
        className="flex h-14 w-14 items-center justify-center rounded-full bg-[#0e7c86] text-white shadow-[0_20px_50px_rgba(14,124,134,0.32)] transition hover:scale-[1.02] hover:bg-[#0c6972]"
        onClick={() => setOpen((current) => !current)}
      >
        <MessageSquareText className="h-6 w-6" />
      </button>
    </div>
  );
}

export function AuroraApp({ initialSection }: { initialSection: SectionKey }) {
  const [section] = useState<SectionKey>(initialSection);
  const [session, setSession] = useState<AuroraSession | null>(null);
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [dashboard, setDashboard] = useState<DashboardBundle>({ progress: emptyProgress, streak: emptyStreak, history: emptyHistory, weeklyReport: emptyWeeklyReport, womenHealth: emptyWomenHealth });
  const [plan, setPlan] = useState<PlanResponse | null>(null);
  const [coachResponse, setCoachResponse] = useState<CoachResponse | null>(null);
  const [authMode, setAuthMode] = useState<"login" | "register">("login");
  const [authError, setAuthError] = useState("");
  const [authBusy, startAuthTransition] = useTransition();
  const [savingProfile, startSavingProfile] = useTransition();
  const [submitting, startSubmitting] = useTransition();
  const [sendingCoach, startSendingCoach] = useTransition();
  const [generatingPlan, startGeneratingPlan] = useTransition();
  const [profileStatus, setProfileStatus] = useState("");
  const [trackingStatus, setTrackingStatus] = useState("");
  const [periodStatus, setPeriodStatus] = useState("");
  const [progressStatus, setProgressStatus] = useState("");
  const [planStatus, setPlanStatus] = useState("");
  const [memoryQuery, setMemoryQuery] = useState("");
  const [memoryResults, setMemoryResults] = useState<Array<Record<string, unknown>>>([]);
  const [memoryLoading, setMemoryLoading] = useState(false);
  const [coachPrompt, setCoachPrompt] = useState("Give me a simple plan for staying consistent this week.");
  const [profileDraft, setProfileDraft] = useProfileDraft(profile, session);
  const [workoutForm, setWorkoutForm] = useState<WorkoutFormState>(buildWorkoutForm);
  const [dietForm, setDietForm] = useState<DietFormState>(buildDietForm);
  const [progressForm, setProgressForm] = useState<ProgressFormState>(buildProgressForm);
  const [feedbackForm, setFeedbackForm] = useState<FeedbackFormState>(buildFeedbackForm);
  const [checkinForm, setCheckinForm] = useState<CheckinFormState>(buildCheckinForm);
  const [periodForm, setPeriodForm] = useState<PeriodFormState>(buildPeriodForm);

  const setDashboardSlice = useCallback((next: Partial<DashboardBundle>) => {
    setDashboard((current) => ({ ...current, ...next }));
  }, []);

  const refreshProfileOnly = useCallback(async (token: string) => {
    const nextProfile = await backendRequest<UserProfile>("/profile/me", token);
    setProfile(nextProfile);
  }, []);

  const refreshWorkspace = useCallback(async (token: string) => {
    const [profileResult, progressResult, streakResult, historyResult, weeklyResult, womenResult] = await Promise.allSettled([
      backendRequest<UserProfile>("/profile/me", token),
      backendRequest<ProgressSummary>("/progress/me", token),
      backendRequest<StreakSummary>("/streaks/me", token),
      backendRequest<HistoryResponse>("/tracking/history", token),
      backendRequest<WeeklyReport>("/tracking/weekly-report", token),
      backendRequest<WomenHealthDashboard>("/women-health/dashboard", token),
    ]);

    if (profileResult.status === "fulfilled") setProfile(profileResult.value);
    else if (normalizeError(profileResult.reason).toLowerCase().includes("not found")) setProfile(null);
    else throw profileResult.reason;

    setDashboard({
      progress: progressResult.status === "fulfilled" ? progressResult.value : emptyProgress,
      streak: streakResult.status === "fulfilled" ? streakResult.value : emptyStreak,
      history: historyResult.status === "fulfilled" ? historyResult.value : emptyHistory,
      weeklyReport: weeklyResult.status === "fulfilled" ? weeklyResult.value : emptyWeeklyReport,
      womenHealth: womenResult.status === "fulfilled" ? womenResult.value : emptyWomenHealth,
    });
    setMemoryResults(historyResult.status === "fulfilled" ? historyResult.value.recent_memories : []);
  }, []);

  const refreshTrackingWorkspace = useCallback(async (token: string) => {
    const [historyResult, weeklyResult, streakResult] = await Promise.allSettled([
      backendRequest<HistoryResponse>("/tracking/history", token),
      backendRequest<WeeklyReport>("/tracking/weekly-report", token),
      backendRequest<StreakSummary>("/streaks/me", token),
    ]);

    setDashboardSlice({
      history: historyResult.status === "fulfilled" ? historyResult.value : emptyHistory,
      weeklyReport: weeklyResult.status === "fulfilled" ? weeklyResult.value : emptyWeeklyReport,
      streak: streakResult.status === "fulfilled" ? streakResult.value : dashboard.streak,
    });

    setMemoryResults(historyResult.status === "fulfilled" ? historyResult.value.recent_memories : []);
  }, [dashboard.streak, setDashboardSlice]);

  const refreshProgressWorkspace = useCallback(async (token: string) => {
    const [progressResult, historyResult, weeklyResult] = await Promise.allSettled([
      backendRequest<ProgressSummary>("/progress/me", token),
      backendRequest<HistoryResponse>("/tracking/history", token),
      backendRequest<WeeklyReport>("/tracking/weekly-report", token),
    ]);

    setDashboardSlice({
      progress: progressResult.status === "fulfilled" ? progressResult.value : emptyProgress,
      history: historyResult.status === "fulfilled" ? historyResult.value : emptyHistory,
      weeklyReport: weeklyResult.status === "fulfilled" ? weeklyResult.value : emptyWeeklyReport,
    });

    setMemoryResults(historyResult.status === "fulfilled" ? historyResult.value.recent_memories : []);
  }, [setDashboardSlice]);

  const refreshWomenHealthWorkspace = useCallback(async (token: string) => {
    const [womenResult, historyResult, weeklyResult] = await Promise.allSettled([
      backendRequest<WomenHealthDashboard>("/women-health/dashboard", token),
      backendRequest<HistoryResponse>("/tracking/history", token),
      backendRequest<WeeklyReport>("/tracking/weekly-report", token),
    ]);

    setDashboardSlice({
      womenHealth: womenResult.status === "fulfilled" ? womenResult.value : emptyWomenHealth,
      history: historyResult.status === "fulfilled" ? historyResult.value : emptyHistory,
      weeklyReport: weeklyResult.status === "fulfilled" ? weeklyResult.value : emptyWeeklyReport,
    });

    setMemoryResults(historyResult.status === "fulfilled" ? historyResult.value.recent_memories : []);
  }, [setDashboardSlice]);

  useEffect(() => {
    const existing = getStoredSession();
    if (existing) setSession(existing);
  }, []);

  useEffect(() => {
    if (!session) return;
    let active = true;
    (async () => {
      try {
        await refreshWorkspace(session.token);
      } catch (error) {
        if (active) setAuthError(normalizeError(error));
      }
    })();
    return () => {
      active = false;
    };
  }, [refreshWorkspace, session]);

  useEffect(() => {
    if (!session) return;
    if (memoryQuery.trim().length < 2) {
      setMemoryResults(dashboard.history.recent_memories);
      setMemoryLoading(false);
      return;
    }

    let active = true;
    setMemoryLoading(true);
    const timer = window.setTimeout(async () => {
      try {
        const result = await backendRequest<{ query: string; results: Array<Record<string, unknown>> }>("/tracking/memory-search", session.token, {
          method: "POST",
          body: JSON.stringify({ query: memoryQuery.trim(), top_k: 8 }),
        });
        if (active) setMemoryResults(result.results);
      } catch {
        if (active) setMemoryResults([]);
      } finally {
        if (active) setMemoryLoading(false);
      }
    }, 350);

    return () => {
      active = false;
      window.clearTimeout(timer);
    };
  }, [dashboard.history.recent_memories, memoryQuery, session]);

  async function handleAuthSubmit(payload: Record<string, string>) {
    setAuthError("");
    startAuthTransition(async () => {
      try {
        const nextSession = authMode === "login" ? await loginLocalSession({ email: payload.email, password: payload.password }) : await registerLocalSession({ name: payload.name, username: payload.username, email: payload.email, password: payload.password });
        setSession(nextSession);
      } catch (error) {
        setAuthError(normalizeError(error));
      }
    });
  }

  function logout() {
    clearStoredSession();
    setSession(null);
    setProfile(null);
    setPlan(null);
    setCoachResponse(null);
    setAuthError("");
  }

  async function saveProfile() {
    if (!session) return;
    setProfileStatus("");
    startSavingProfile(async () => {
      try {
        await backendRequest<Record<string, unknown>>("/profile", session.token, { method: "POST", body: JSON.stringify(profileDraft) });
        setProfileStatus("Profile saved successfully.");
        await refreshProfileOnly(session.token);
      } catch (error) {
        setProfileStatus(normalizeError(error));
      }
    });
  }

  async function generatePlan() {
    if (!profile) {
      setPlanStatus("Save the profile first so the plan has real inputs.");
      return;
    }
    setPlanStatus("");
    startGeneratingPlan(async () => {
      try {
        const generated = await publicBackendRequest<PlanResponse>("/generate-plan", {
          method: "POST",
          body: JSON.stringify({
            goal: profile.goal,
            level: profile.level,
            weight: profile.weight,
            gender: profile.gender,
            cycle_phase: dashboard.womenHealth.predicted_phase,
            age: profile.age,
            activity_level: profile.lifestyle.activity_level,
            pregnant: profile.pregnant,
            postpartum: profile.postpartum,
            pregnancy_trimester: profile.pregnancy_trimester,
            postpartum_weeks: profile.postpartum_weeks,
            hormonal_concerns: profile.hormonal_concerns,
            dietary_restrictions: profile.dietary_restrictions,
          }),
        });
        setPlan(generated);
        setPlanStatus("Plan refreshed from the backend.");
      } catch (error) {
        setPlanStatus(normalizeError(error));
      }
    });
  }

  async function submitWorkout() {
    if (!session) return;
    setTrackingStatus("");
    startSubmitting(async () => {
      try {
        await backendRequest<Record<string, unknown>>("/tracking/workout", session.token, { method: "POST", body: JSON.stringify(workoutForm) });
        setWorkoutForm(buildWorkoutForm());
        setTrackingStatus("Workout log saved.");
        await refreshTrackingWorkspace(session.token);
      } catch (error) {
        setTrackingStatus(normalizeError(error));
      }
    });
  }

  async function submitDiet() {
    if (!session) return;
    setTrackingStatus("");
    startSubmitting(async () => {
      try {
        await backendRequest<Record<string, unknown>>("/tracking/diet", session.token, { method: "POST", body: JSON.stringify({ ...dietForm, cravings: parseList(dietForm.cravings) }) });
        setDietForm(buildDietForm());
        setTrackingStatus("Diet log saved.");
        await refreshTrackingWorkspace(session.token);
      } catch (error) {
        setTrackingStatus(normalizeError(error));
      }
    });
  }

  async function submitFeedback() {
    if (!session) return;
    setTrackingStatus("");
    startSubmitting(async () => {
      try {
        await backendRequest<Record<string, unknown>>("/tracking/feedback", session.token, { method: "POST", body: JSON.stringify(feedbackForm) });
        setFeedbackForm(buildFeedbackForm());
        setTrackingStatus("Feedback saved.");
        await refreshTrackingWorkspace(session.token);
      } catch (error) {
        setTrackingStatus(normalizeError(error));
      }
    });
  }

  async function submitCheckin() {
    if (!session) return;
    setTrackingStatus("");
    startSubmitting(async () => {
      try {
        await backendRequest<Record<string, unknown>>("/streaks/check-in", session.token, { method: "POST", body: JSON.stringify(checkinForm) });
        setCheckinForm(buildCheckinForm());
        setTrackingStatus("Daily check-in saved.");
        await refreshTrackingWorkspace(session.token);
      } catch (error) {
        setTrackingStatus(normalizeError(error));
      }
    });
  }

  async function submitProgress() {
    if (!session) return;
    setProgressStatus("");
    startSubmitting(async () => {
      try {
        await backendRequest<Record<string, unknown>>("/progress/log", session.token, { method: "POST", body: JSON.stringify(progressForm) });
        setProgressForm(buildProgressForm());
        setProgressStatus("Progress log saved.");
        await refreshProgressWorkspace(session.token);
      } catch (error) {
        setProgressStatus(normalizeError(error));
      }
    });
  }

  async function submitPeriod() {
    if (!session) return;
    setPeriodStatus("");
    startSubmitting(async () => {
      try {
        await backendRequest<Record<string, unknown>>("/women-health/log-period", session.token, { method: "POST", body: JSON.stringify({ ...periodForm, symptoms: parseList(periodForm.symptoms), cravings: parseList(periodForm.cravings) }) });
        setPeriodForm(buildPeriodForm());
        setPeriodStatus("Period log saved.");
        await refreshWomenHealthWorkspace(session.token);
      } catch (error) {
        setPeriodStatus(normalizeError(error));
      }
    });
  }

  async function askCoach() {
    if (!session) return;
    startSendingCoach(async () => {
      try {
        const response = await backendRequest<CoachResponse>("/progress/coach", session.token, { method: "POST", body: JSON.stringify({ message: coachPrompt }) });
        setCoachResponse(response);
      } catch (error) {
        setCoachResponse({ reply: normalizeError(error), insights: [], next_steps: [] });
      }
    });
  }

  if (!session) return <AuthScreen mode={authMode} onModeChange={setAuthMode} onSubmit={handleAuthSubmit} busy={authBusy} error={authError} />;

  if (!profile && section !== "profile") {
    return (
      <>
        <AppFrame session={session} currentSection="profile" onLogout={logout}>
          <ProfileSection draft={profileDraft} setDraft={setProfileDraft} saving={savingProfile} submitLabel="Save profile and continue" status={profileStatus || "Complete your profile once so Aurora can personalize the rest of the app."} onSave={saveProfile} />
        </AppFrame>
        <AuroraAssistant section="profile" session={session} profile={profile} />
      </>
    );
  }

  const currentProfile = profile ?? profileDraft;
  let content: ReactNode;
  switch (section) {
    case "profile":
      content = <ProfileSection draft={profileDraft} setDraft={setProfileDraft} saving={savingProfile} submitLabel={profile ? "Update profile" : "Save profile and continue"} status={profileStatus} onSave={saveProfile} />;
      break;
    case "plans":
      content = <PlansSection profile={currentProfile} womenHealth={dashboard.womenHealth} plan={plan} generating={generatingPlan} planStatus={planStatus} onGenerate={generatePlan} />;
      break;
    case "tracking":
      content = <TrackingSection history={dashboard.history} workoutForm={workoutForm} setWorkoutForm={setWorkoutForm} dietForm={dietForm} setDietForm={setDietForm} feedbackForm={feedbackForm} setFeedbackForm={setFeedbackForm} checkinForm={checkinForm} setCheckinForm={setCheckinForm} trackingStatus={trackingStatus} submitting={submitting} onSubmitWorkout={submitWorkout} onSubmitDiet={submitDiet} onSubmitFeedback={submitFeedback} onSubmitCheckin={submitCheckin} />;
      break;
    case "progress":
      content = <ProgressSection progress={dashboard.progress} form={progressForm} setForm={setProgressForm} progressStatus={progressStatus} submitting={submitting} onSubmit={submitProgress} />;
      break;
    case "women-health":
      content = <WomenHealthSection womenHealth={dashboard.womenHealth} periodForm={periodForm} setPeriodForm={setPeriodForm} periodStatus={periodStatus} submitting={submitting} onSubmit={submitPeriod} />;
      break;
    case "memory":
      content = <MemorySection history={dashboard.history} memoryQuery={memoryQuery} setMemoryQuery={setMemoryQuery} memoryResults={memoryResults} memoryLoading={memoryLoading} />;
      break;
    case "reports":
      content = <ReportsSection report={dashboard.weeklyReport} />;
      break;
    case "coach":
      content = <CoachSection prompt={coachPrompt} setPrompt={setCoachPrompt} response={coachResponse} sending={sendingCoach} onSend={askCoach} />;
      break;
    case "home":
    default:
      content = <HomeSection profile={currentProfile} data={dashboard} onOpenSection={(nextSection) => {
        const item = navItems.find((entry) => entry.key === nextSection);
        if (item) window.location.assign(item.href);
      }} />;
      break;
  }

  return (
    <>
      <AppFrame session={session} currentSection={section} onLogout={logout}>
        <div className="space-y-6 pb-28 xl:pb-10">
          <div className="rounded-[32px] border border-white/70 bg-[rgba(252,255,253,0.8)] p-4 shadow-[0_20px_60px_rgba(10,26,35,0.08)] backdrop-blur xl:hidden">
            <div className="flex gap-3 overflow-x-auto pb-1">
              {navItems.map((item) => <Link key={item.key} href={item.href} className={`chip whitespace-nowrap ${item.key === section ? "bg-[#0e7c86] text-white" : ""}`}>{item.label}</Link>)}
            </div>
          </div>
          {content}
        </div>
      </AppFrame>
      <AuroraAssistant section={section} session={session} profile={profile} />
    </>
  );
}
