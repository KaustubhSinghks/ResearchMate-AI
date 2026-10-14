"use client";

import { motion } from "framer-motion";
import { LucideIcon } from "lucide-react";

export default function StatTile({
  label,
  value,
  icon: Icon,
  accent = "brand",
  delay = 0,
}: {
  label: string;
  value: number | string;
  icon: LucideIcon;
  accent?: "brand" | "emerald" | "amber" | "red";
  delay?: number;
}) {
  const accentClasses: Record<string, string> = {
    brand: "from-brand-500 to-fuchsia-500 text-brand-500",
    emerald: "from-emerald-400 to-teal-500 text-emerald-500",
    amber: "from-amber-400 to-orange-500 text-amber-500",
    red: "from-rose-400 to-red-500 text-rose-500",
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay, ease: "easeOut" }}
      className="card card-hover relative overflow-hidden p-5"
    >
      <div
        className={`absolute -right-6 -top-6 h-20 w-20 rounded-full bg-gradient-to-br opacity-20 blur-2xl ${accentClasses[accent]}`}
      />
      <div className="relative flex items-center justify-between">
        <div>
          <div className="text-2xl font-semibold text-ink">{value}</div>
          <div className="mt-1 text-xs font-medium text-ink-muted">{label}</div>
        </div>
        <div
          className={`flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br ${accentClasses[accent]} bg-opacity-10`}
        >
          <Icon className={`h-5 w-5 ${accentClasses[accent].split(" ").pop()}`} strokeWidth={2} />
        </div>
      </div>
    </motion.div>
  );
}
