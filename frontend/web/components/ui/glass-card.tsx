"use client";

import { motion } from "framer-motion";
import { clsx } from "clsx";
import type { HTMLMotionProps } from "framer-motion";
import type { ReactNode } from "react";

export function GlassCard({
  children,
  className,
  ...props
}: HTMLMotionProps<"div"> & { children: ReactNode }) {
  return (
    <motion.div
      whileHover={{ y: -4 }}
      transition={{ duration: 0.28, ease: "easeOut" }}
      className={clsx("glass-card gradient-border relative p-6", className)}
      {...props}
    >
      {children}
    </motion.div>
  );
}
