"use client";

import { motion } from "framer-motion";
import { clsx } from "clsx";
import type { HTMLMotionProps } from "framer-motion";
import type { ReactNode } from "react";

type GradientButtonProps = HTMLMotionProps<"button"> & {
  children: ReactNode;
  variant?: "primary" | "ghost";
};

export function GradientButton({
  children,
  className,
  variant = "primary",
  ...props
}: GradientButtonProps) {
  return (
    <motion.button
      whileHover={{ scale: 1.03, y: -2 }}
      whileTap={{ scale: 0.98 }}
      className={clsx(
        "inline-flex items-center justify-center gap-2 rounded-full px-5 py-3 text-sm font-semibold transition-all duration-300",
        variant === "primary"
          ? "bg-aurora-gradient text-white shadow-neon"
          : "border border-white/10 bg-white/5 text-white/80 hover:bg-white/10",
        className,
      )}
      {...props}
    >
      {children}
    </motion.button>
  );
}
