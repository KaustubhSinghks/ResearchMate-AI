"use client";

import { motion } from "framer-motion";
import { ReactNode } from "react";

export default function PageHeader({
  title,
  description,
  actions,
}: {
  title: string;
  description?: string;
  actions?: ReactNode;
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: -8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.35, ease: "easeOut" }}
      className="mb-8 flex flex-wrap items-start justify-between gap-4"
    >
      <div>
        <h1 className="text-2xl font-semibold tracking-tight text-ink sm:text-3xl">{title}</h1>
        {description && <p className="mt-1.5 text-sm text-ink-muted">{description}</p>}
      </div>
      {actions && <div className="flex items-center gap-2">{actions}</div>}
    </motion.div>
  );
}
