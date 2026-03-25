"use client";

import { motion, AnimatePresence } from "framer-motion";
import { GlassCard } from "@/components/ui/glass-card";

export function AIFeedbackBox({
  title,
  feedback,
}: {
  title: string;
  feedback: string[];
}) {
  return (
    <GlassCard className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <p className="section-label">{title}</p>
          <h3 className="mt-2 text-2xl font-semibold">Aurora is coaching live</h3>
        </div>
        <span className="inline-flex h-3 w-3 animate-pulse rounded-full bg-emerald-300 shadow-[0_0_24px_rgba(140,255,122,0.75)]" />
      </div>
      <div className="space-y-3">
        <AnimatePresence mode="popLayout">
          {feedback.map((item, index) => (
            <motion.div
              key={`${item}-${index}`}
              initial={{ opacity: 0, x: 18 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -12 }}
              transition={{ duration: 0.35, delay: index * 0.08 }}
              className="rounded-2xl border border-cyan-300/10 bg-white/5 px-4 py-3 text-sm text-white/70"
            >
              {item}
            </motion.div>
          ))}
        </AnimatePresence>
      </div>
    </GlassCard>
  );
}
