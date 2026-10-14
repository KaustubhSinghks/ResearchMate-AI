"use client";

import { motion } from "framer-motion";
import { Moon, Sun } from "lucide-react";
import { useTheme } from "@/lib/theme";

export default function ThemeToggle() {
  const { theme, toggleTheme } = useTheme();
  const isDark = theme === "dark";

  return (
    <button
      onClick={toggleTheme}
      aria-label="Toggle theme"
      className="relative flex h-8 w-14 items-center rounded-full border border-border bg-surface-raised px-1 transition-colors duration-300"
    >
      <motion.div
        className="flex h-6 w-6 items-center justify-center rounded-full bg-brand-gradient shadow-md"
        animate={{ x: isDark ? 24 : 0 }}
        transition={{ type: "spring", stiffness: 500, damping: 30 }}
      >
        {isDark ? <Moon className="h-3.5 w-3.5 text-white" /> : <Sun className="h-3.5 w-3.5 text-white" />}
      </motion.div>
    </button>
  );
}
