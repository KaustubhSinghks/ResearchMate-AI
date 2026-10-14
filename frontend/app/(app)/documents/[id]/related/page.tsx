"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import { Sparkles, BookOpen, Quote as QuoteIcon, ThumbsUp, ExternalLink } from "lucide-react";
import { api } from "@/lib/api";
import { RelatedPaper } from "@/lib/types";
import PageHeader from "@/components/PageHeader";
import Skeleton from "@/components/Skeleton";

const TABS = [
  { key: "similar", label: "Similar", icon: Sparkles },
  { key: "references", label: "References", icon: BookOpen },
  { key: "citing", label: "Cited by", icon: QuoteIcon },
  { key: "recommended", label: "Recommended", icon: ThumbsUp },
] as const;

export default function RelatedPapersPage() {
  const params = useParams<{ id: string }>();
  const documentId = Number(params.id);

  const [tab, setTab] = useState<(typeof TABS)[number]["key"]>("similar");
  const [papers, setPapers] = useState<RelatedPaper[] | null>(null);

  useEffect(() => {
    setPapers(null);
    api.get<RelatedPaper[]>(`/documents/${documentId}/related/${tab}`).then(setPapers);
  }, [documentId, tab]);

  return (
    <div>
      <PageHeader title="Related papers" description="Explore the citation network and similar work" />

      <div className="mb-6 flex flex-wrap gap-2">
        {TABS.map(({ key, label, icon: Icon }) => {
          const active = tab === key;
          return (
            <button
              key={key}
              onClick={() => setTab(key)}
              className={`relative flex items-center gap-1.5 rounded-xl px-3.5 py-2 text-sm font-medium transition-colors ${
                active ? "text-white" : "border border-border text-ink-muted hover:text-ink"
              }`}
            >
              {active && (
                <motion.div
                  layoutId="related-tab-pill"
                  className="absolute inset-0 rounded-xl bg-brand-gradient shadow-md shadow-brand-500/25"
                  transition={{ type: "spring", stiffness: 400, damping: 32 }}
                />
              )}
              <Icon className="relative h-3.5 w-3.5" />
              <span className="relative">{label}</span>
            </button>
          );
        })}
      </div>

      {papers === null ? (
        <div className="space-y-2">
          {Array.from({ length: 4 }).map((_, i) => (
            <Skeleton key={i} className="h-16" />
          ))}
        </div>
      ) : papers.length === 0 ? (
        <p className="text-ink-muted">Nothing found for this category.</p>
      ) : (
        <ul className="space-y-2">
          <AnimatePresence mode="wait">
            {papers.map((p, i) => (
              <motion.li
                key={`${tab}-${i}`}
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3, delay: i * 0.03 }}
                className="card card-hover p-4"
              >
                <p className="font-medium text-ink">
                  {p.url ? (
                    <a
                      href={p.url}
                      target="_blank"
                      rel="noreferrer"
                      className="inline-flex items-center gap-1.5 hover:text-brand-500"
                    >
                      {p.title}
                      <ExternalLink className="h-3 w-3" />
                    </a>
                  ) : (
                    p.title
                  )}
                </p>
                <p className="mt-1 text-xs text-ink-faint">
                  {(p.authors ?? []).join(", ")} {p.year ? `· ${p.year}` : ""}
                  {p.score != null ? ` · similarity ${(p.score * 100).toFixed(0)}%` : ""}
                </p>
              </motion.li>
            ))}
          </AnimatePresence>
        </ul>
      )}
    </div>
  );
}
