"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import { FileText } from "lucide-react";
import { DocumentListItem } from "@/lib/types";
import StatusBadge from "./StatusBadge";

export default function DocumentCard({ doc, index = 0 }: { doc: DocumentListItem; index?: number }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.35, delay: Math.min(index * 0.04, 0.4), ease: "easeOut" }}
    >
      <Link href={`/documents/${doc.id}`} className="card card-hover group block p-4">
        <div className="flex items-start gap-3">
          <div className="mt-0.5 flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-brand-gradient-soft text-brand-500">
            <FileText className="h-4 w-4" />
          </div>
          <div className="min-w-0 flex-1">
            <div className="flex items-start justify-between gap-2">
              <h3 className="truncate font-medium text-ink transition-colors group-hover:text-brand-500">
                {doc.title}
              </h3>
            </div>
            <p className="mt-0.5 text-xs text-ink-faint">
              {doc.venue ?? "Unknown venue"} {doc.year ? `· ${doc.year}` : ""}
            </p>
          </div>
          <StatusBadge status={doc.status} />
        </div>
        {doc.short_summary && (
          <p className="mt-3 line-clamp-2 text-sm text-ink-muted">{doc.short_summary}</p>
        )}
      </Link>
    </motion.div>
  );
}
