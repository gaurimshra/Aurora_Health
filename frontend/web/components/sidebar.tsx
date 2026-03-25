"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { AnimatePresence, motion } from "framer-motion";
import { clsx } from "clsx";
import { BarChart3, Brain, ClipboardList, Dumbbell, LayoutDashboard, ScanHeart, Sparkles, TimerReset, UserRound, WandSparkles } from "lucide-react";
import { GradientButton } from "@/components/ui/gradient-button";

const items = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/workout", label: "Workout", icon: Dumbbell },
  { href: "/progress", label: "Progress", icon: BarChart3 },
  { href: "/tracking", label: "Tracking", icon: ClipboardList },
  { href: "/memory", label: "Memory", icon: Brain },
  { href: "/coach", label: "Coach", icon: WandSparkles },
  { href: "/profile", label: "Profile", icon: UserRound },
  { href: "/women-health", label: "Women", icon: ScanHeart },
];

export function Sidebar({
  collapsed,
  onToggle,
}: {
  collapsed: boolean;
  onToggle: () => void;
}) {
  const pathname = usePathname();

  return (
    <motion.aside
      layout
      className={clsx(
        "glass-card sticky top-6 flex h-[calc(100vh-3rem)] flex-col justify-between p-4",
        collapsed ? "w-[94px]" : "w-[280px]",
      )}
    >
      <div className="space-y-6">
        <div className="flex items-center justify-between rounded-3xl border border-white/10 bg-white/5 px-4 py-4">
          <div className="flex items-center gap-3">
            <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-aurora-gradient shadow-neon">
              <Sparkles className="h-5 w-5 text-white" />
            </div>
            <AnimatePresence>
              {!collapsed ? (
                <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
                  <p className="text-sm font-semibold text-white">Aurora</p>
                  <p className="text-xs text-white/50">Adaptive fitness OS</p>
                </motion.div>
              ) : null}
            </AnimatePresence>
          </div>
          <button
            type="button"
            onClick={onToggle}
            className="rounded-full border border-white/10 bg-white/5 p-2 text-white/70 transition hover:bg-white/10"
          >
            <TimerReset className="h-4 w-4" />
          </button>
        </div>

        <nav className="space-y-2 overflow-y-auto pr-1">
          {items.map((item) => {
            const Icon = item.icon;
            const active = pathname === item.href;
            return (
              <Link
                key={item.href}
                href={item.href}
                className={clsx(
                  "group flex items-center gap-3 rounded-2xl px-4 py-3 transition",
                  active ? "bg-white/10 text-white" : "text-white/60 hover:bg-white/10 hover:text-white",
                )}
              >
                <Icon className="h-5 w-5" />
                <AnimatePresence>
                  {!collapsed ? (
                    <motion.span initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="text-sm font-medium">
                      {item.label}
                    </motion.span>
                  ) : null}
                </AnimatePresence>
              </Link>
            );
          })}
        </nav>
      </div>

      <div className="space-y-4">
        <AnimatePresence>
          {!collapsed ? (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: 10 }}
              className="rounded-[26px] border border-cyan-300/20 bg-cyan-400/10 p-4"
            >
              <p className="text-xs uppercase tracking-[0.24em] text-cyan-200/70">Motivation</p>
              <p className="mt-3 text-sm text-white/70">You&apos;re getting stronger every day. Stay with the signal.</p>
            </motion.div>
          ) : null}
        </AnimatePresence>
        <Link href="/plans">
          <GradientButton className="w-full">{collapsed ? "Plan" : "Generate Plan"}</GradientButton>
        </Link>
      </div>
    </motion.aside>
  );
}
