import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: "class",
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        sans: ["var(--font-inter)", "system-ui", "sans-serif"],
      },
      colors: {
        surface: {
          DEFAULT: "rgb(var(--surface) / <alpha-value>)",
          raised: "rgb(var(--surface-raised) / <alpha-value>)",
        },
        base: {
          DEFAULT: "rgb(var(--bg) / <alpha-value>)",
        },
        ink: {
          DEFAULT: "rgb(var(--ink) / <alpha-value>)",
          muted: "rgb(var(--ink-muted) / <alpha-value>)",
          faint: "rgb(var(--ink-faint) / <alpha-value>)",
        },
        border: {
          DEFAULT: "rgb(var(--border) / <alpha-value>)",
        },
        brand: {
          50: "#eef2ff",
          100: "#e0e7ff",
          200: "#c7d2fe",
          300: "#a5b4fc",
          400: "#818cf8",
          500: "#6366f1",
          600: "#4f46e5",
          700: "#4338ca",
          800: "#3730a3",
          900: "#312e81",
        },
      },
      backgroundImage: {
        "brand-gradient": "linear-gradient(135deg, #6366f1 0%, #a855f7 50%, #06b6d4 100%)",
        "brand-gradient-soft": "linear-gradient(135deg, #6366f120 0%, #a855f720 50%, #06b6d420 100%)",
        "mesh-dark":
          "radial-gradient(at 20% 0%, rgba(99,102,241,0.25) 0px, transparent 50%), radial-gradient(at 80% 0%, rgba(168,85,247,0.2) 0px, transparent 50%), radial-gradient(at 50% 100%, rgba(6,182,212,0.15) 0px, transparent 50%)",
        "mesh-light":
          "radial-gradient(at 20% 0%, rgba(99,102,241,0.12) 0px, transparent 50%), radial-gradient(at 80% 0%, rgba(168,85,247,0.10) 0px, transparent 50%), radial-gradient(at 50% 100%, rgba(6,182,212,0.08) 0px, transparent 50%)",
      },
      keyframes: {
        "fade-in": {
          "0%": { opacity: "0", transform: "translateY(6px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        blob: {
          "0%, 100%": { transform: "translate(0px, 0px) scale(1)" },
          "33%": { transform: "translate(20px, -30px) scale(1.05)" },
          "66%": { transform: "translate(-15px, 15px) scale(0.98)" },
        },
        shimmer: {
          "0%": { transform: "translateX(-100%)" },
          "100%": { transform: "translateX(100%)" },
        },
      },
      animation: {
        "fade-in": "fade-in 0.4s ease-out",
        blob: "blob 12s infinite ease-in-out",
        shimmer: "shimmer 2s linear infinite",
      },
    },
  },
  plugins: [],
};

export default config;
