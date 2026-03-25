"use client";

import { motion } from "framer-motion";

export function ProgressRing({
  value,
  label,
  size = 150,
}: {
  value: number;
  label: string;
  size?: number;
}) {
  const normalized = Math.max(0, Math.min(100, value));
  const stroke = 10;
  const radius = (size - stroke) / 2;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (normalized / 100) * circumference;

  return (
    <div className="relative inline-flex items-center justify-center">
      <svg width={size} height={size} className="-rotate-90">
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke="rgba(255,255,255,0.1)"
          strokeWidth={stroke}
          fill="transparent"
        />
        <motion.circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke="url(#aurora-ring)"
          strokeWidth={stroke}
          strokeLinecap="round"
          fill="transparent"
          initial={{ strokeDashoffset: circumference }}
          animate={{ strokeDashoffset: offset }}
          transition={{ duration: 1.1, ease: "easeOut" }}
          strokeDasharray={circumference}
        />
        <defs>
          <linearGradient id="aurora-ring" x1="0%" x2="100%" y1="0%" y2="100%">
            <stop offset="0%" stopColor="#865DFF" />
            <stop offset="65%" stopColor="#5EF2FF" />
            <stop offset="100%" stopColor="#8CFF7A" />
          </linearGradient>
        </defs>
      </svg>
      <div className="absolute flex flex-col items-center">
        <span className="text-3xl font-semibold text-white">{normalized}</span>
        <span className="text-xs uppercase tracking-[0.24em] text-cyan-100/60">{label}</span>
      </div>
    </div>
  );
}
