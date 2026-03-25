"use client";

import { motion, animate, useMotionValue, useTransform } from "framer-motion";
import { useEffect } from "react";
import { GlassCard } from "@/components/ui/glass-card";

export function StatCard({
  label,
  value,
  suffix = "",
  detail,
  accent,
}: {
  label: string;
  value: number;
  suffix?: string;
  detail: string;
  accent?: string;
}) {
  const count = useMotionValue(0);
  const rounded = useTransform(count, (latest) => Math.round(latest));

  useEffect(() => {
    const controls = animate(count, value, { duration: 1.2, ease: "easeOut" });
    return () => controls.stop();
  }, [count, value]);

  return (
    <GlassCard className="group overflow-hidden">
      <div
        className="pointer-events-none absolute inset-x-6 top-0 h-24 rounded-b-full blur-3xl"
        style={{ background: accent ?? "rgba(94,242,255,0.14)" }}
      />
      <div className="relative space-y-4">
        <p className="section-label">{label}</p>
        <motion.div className="text-4xl font-semibold text-white">
          <motion.span>{rounded}</motion.span>
          <span className="text-lg text-white/50">{suffix}</span>
        </motion.div>
        <p className="max-w-[18rem] text-white/60">{detail}</p>
      </div>
    </GlassCard>
  );
}
