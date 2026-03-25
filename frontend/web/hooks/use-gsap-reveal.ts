"use client";

import { useEffect, useRef } from "react";
import gsap from "gsap";

export function useGsapReveal<T extends HTMLElement>(deps: unknown[] = []) {
  const ref = useRef<T | null>(null);

  useEffect(() => {
    if (!ref.current) {
      return;
    }

    const ctx = gsap.context(() => {
      gsap.fromTo(
        ref.current,
        { opacity: 0, y: 24 },
        { opacity: 1, y: 0, duration: 0.9, ease: "power3.out" },
      );
    }, ref);

    return () => ctx.revert();
  }, deps);

  return ref;
}
