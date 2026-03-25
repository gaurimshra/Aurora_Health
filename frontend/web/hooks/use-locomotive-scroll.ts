"use client";

import { useEffect } from "react";

export function useLocomotiveScroll(enabled = true) {
  useEffect(() => {
    if (!enabled) {
      return;
    }

    let scroll: { destroy: () => void } | undefined;

    void import("locomotive-scroll").then((module) => {
      const LocomotiveScroll = module.default;
      scroll = new LocomotiveScroll({
        el: document.querySelector("[data-scroll-container]") as HTMLElement,
        smooth: true,
        lerp: 0.08,
        smartphone: { smooth: true },
        tablet: { smooth: true },
      });
    });

    return () => {
      scroll?.destroy();
    };
  }, [enabled]);
}
