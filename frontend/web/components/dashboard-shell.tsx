"use client";

import { ReactNode, useMemo, useState } from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import { ArrowUpRight, Bell } from "lucide-react";
import { Sidebar } from "@/components/sidebar";
import { GradientButton } from "@/components/ui/gradient-button";

export function DashboardShell({
  title,
  eyebrow,
  description,
  headerStats,
  children,
}: {
  title: string;
  eyebrow: string;
  description: string;
  headerStats?: Array<{ label: string; value: string }>;
  children: ReactNode;
}) {
  const [collapsed, setCollapsed] = useState(false);
  const fallbackHeaderStats = useMemo(
    () => [
      { label: "Focus", value: "Adaptive Coaching" },
      { label: "Realtime", value: "Motion + Recovery" },
      { label: "Identity", value: "Local Session Ready" },
    ],
    [],
  );

  return (
    <div className="page-grid">
      <div className="grid gap-6 lg:grid-cols-[auto,1fr]">
        <Sidebar collapsed={collapsed} onToggle={() => setCollapsed((value) => !value)} />

        <div className="space-y-6">
          <div className="glass-card flex flex-col gap-6 p-6 lg:flex-row lg:items-center lg:justify-between">
            <div className="space-y-4">
              <p className="section-label">{eyebrow}</p>
              <div>
                <h1 className="text-4xl font-semibold md:text-5xl">{title}</h1>
                <p className="mt-4 max-w-2xl text-white/60">{description}</p>
              </div>
              <div className="flex flex-wrap gap-3">
                {(headerStats ?? fallbackHeaderStats).map((item) => (
                  <div key={item.label} className="rounded-full border border-white/10 bg-white/5 px-4 py-2 text-xs text-white/70">
                    <span className="mr-2 text-white/40">{item.label}</span>
                    <span>{item.value}</span>
                  </div>
                ))}
              </div>
            </div>

            <div className="flex items-center gap-3 self-start lg:self-center">
              <button type="button" className="rounded-full border border-white/10 bg-white/10 p-3 text-white/70">
                <Bell className="h-4 w-4" />
              </button>
              <Link href="/workout">
                <GradientButton>
                  Start Session
                  <ArrowUpRight className="h-4 w-4" />
                </GradientButton>
              </Link>
              <motion.div whileHover={{ scale: 1.04 }}>
                <div className="rounded-full border border-white/10 bg-white/5 px-4 py-2 text-xs uppercase tracking-[0.18em] text-white/60">
                  Live Workspace
                </div>
              </motion.div>
            </div>
          </div>

          {children}
        </div>
      </div>
    </div>
  );
}
