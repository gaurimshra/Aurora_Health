import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
    "./hooks/**/*.{ts,tsx}",
    "./animations/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        aurora: {
          bg: "#060816",
          panel: "#0c1023",
          border: "rgba(255,255,255,0.12)",
          cyan: "#5EF2FF",
          green: "#8CFF7A",
          purple: "#865DFF",
          blue: "#3B82F6",
        },
      },
      fontFamily: {
        sans: ["Inter", "Poppins", "system-ui", "sans-serif"],
      },
      boxShadow: {
        glow: "0 0 0 1px rgba(94, 242, 255, 0.18), 0 22px 80px rgba(59, 130, 246, 0.16)",
        neon: "0 0 40px rgba(94, 242, 255, 0.2)",
      },
      backgroundImage: {
        "aurora-gradient":
          "linear-gradient(135deg, rgba(134,93,255,0.95) 0%, rgba(59,130,246,0.92) 55%, rgba(94,242,255,0.85) 100%)",
      },
      animation: {
        float: "float 10s ease-in-out infinite",
        pulseSoft: "pulseSoft 2.5s ease-in-out infinite",
        orbit: "orbit 18s linear infinite",
      },
      keyframes: {
        float: {
          "0%, 100%": { transform: "translateY(0px)" },
          "50%": { transform: "translateY(-14px)" },
        },
        pulseSoft: {
          "0%, 100%": { boxShadow: "0 0 0 rgba(94, 242, 255, 0)" },
          "50%": { boxShadow: "0 0 34px rgba(94, 242, 255, 0.22)" },
        },
        orbit: {
          "0%": { transform: "rotate(0deg) translateX(10px) rotate(0deg)" },
          "100%": { transform: "rotate(360deg) translateX(10px) rotate(-360deg)" },
        },
      },
    },
  },
  plugins: [],
};

export default config;
