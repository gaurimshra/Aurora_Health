"use client";

import { motion } from "framer-motion";

export function MotionBackground() {
  return (
    <div className="pointer-events-none absolute inset-0 overflow-hidden">
      <motion.div
        className="absolute left-[6%] top-[10%] h-72 w-72 rounded-full bg-fuchsia-500/20 blur-3xl"
        animate={{ x: [0, 30, -10, 0], y: [0, -20, 12, 0] }}
        transition={{ duration: 14, repeat: Infinity, ease: "easeInOut" }}
      />
      <motion.div
        className="absolute right-[10%] top-[18%] h-80 w-80 rounded-full bg-cyan-400/20 blur-3xl"
        animate={{ x: [0, -20, 12, 0], y: [0, 18, -10, 0] }}
        transition={{ duration: 16, repeat: Infinity, ease: "easeInOut" }}
      />
      <motion.div
        className="absolute bottom-[8%] left-[28%] h-96 w-96 rounded-full bg-emerald-300/10 blur-3xl"
        animate={{ scale: [1, 1.08, 0.98, 1], opacity: [0.4, 0.7, 0.45, 0.4] }}
        transition={{ duration: 18, repeat: Infinity, ease: "easeInOut" }}
      />
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,rgba(255,255,255,0.04),transparent_45%)]" />
    </div>
  );
}
