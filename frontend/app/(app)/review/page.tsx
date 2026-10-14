"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { BookOpen, Sparkles, Loader2 } from "lucide-react";
import { api } from "@/lib/api";
import { DocumentListItem, ReviewResult } from "@/lib/types";
import PageHeader from "@/components/PageHeader";

export default function ReviewPage() {
  const [documents, setDocuments] = useState<DocumentListItem[]>([]);
  const [selected, setSelected] = useState<Set<number>>(new Set());
  const [title, setTitle] = useState("");
  const [reviews, setReviews] = useState<ReviewResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.get<DocumentListItem[]>("/documents").then(setDocuments);
    api.get<ReviewResult[]>("/review").then(setReviews);
  }, []);

  function toggle(id: number) {
    setSelected((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  }

  async function generate(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    if (!title.trim() || selected.size === 0) {
      setError("Give it a title and select at least one document.");
      return;
    }
    setLoading(true);
    try {
      const review = await api.post<ReviewResult>("/review", {
        title,
        document_ids: Array.from(selected),
      });
      setReviews((prev) => [review, ...prev]);
      setTitle("");
      setSelected(new Set());
    } catch {
      setError("Failed to generate review support.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div>
      <PageHeader title="Literature review support" description="Group papers, find gaps, and draft an outline" />

      <form onSubmit={generate} className="card mb-10 p-5">
        <input
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="Review title, e.g. 'RAG methods for scientific QA'"
          className="input-field mb-4 max-w-md"
        />
        <div className="mb-4 grid grid-cols-2 gap-2">
          {documents.map((doc) => {
            const checked = selected.has(doc.id);
            return (
              <label
                key={doc.id}
                className={`flex cursor-pointer items-center gap-2.5 rounded-xl border p-2.5 text-sm transition-colors ${
                  checked ? "border-brand-400/60 bg-brand-gradient-soft" : "border-border"
                }`}
              >
                <input type="checkbox" checked={checked} onChange={() => toggle(doc.id)} className="accent-brand-500" />
                <span className="text-ink">{doc.title}</span>
              </label>
            );
          })}
        </div>
        {error && <p className="mb-4 text-sm text-red-500">{error}</p>}
        <button type="submit" disabled={loading} className="btn-primary">
          {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Sparkles className="h-4 w-4" />}
          {loading ? "Generating..." : "Generate review support"}
        </button>
      </form>

      <div className="space-y-6">
        {reviews.map((review, i) => (
          <motion.div
            key={review.id}
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: Math.min(i * 0.05, 0.3) }}
            className="card p-5"
          >
            <div className="mb-4 flex items-center gap-2">
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-brand-gradient-soft text-brand-500">
                <BookOpen className="h-4 w-4" />
              </div>
              <h2 className="text-lg font-medium text-ink">{review.title}</h2>
            </div>

            {review.trends && Object.keys(review.trends).length > 0 && (
              <Section label="Trends over time">
                <div className="flex flex-wrap gap-2 text-sm">
                  {Object.entries(review.trends).map(([year, count]) => (
                    <span key={year} className="rounded-full bg-surface-raised px-2.5 py-1 text-ink-muted">
                      {year}: {count}
                    </span>
                  ))}
                </div>
              </Section>
            )}

            {review.themes && Object.keys(review.themes).length > 0 && (
              <Section label="Themes">
                <ul className="space-y-1">
                  {Object.entries(review.themes).map(([theme, ids]) => (
                    <li key={theme} className="flex items-center gap-2 text-sm text-ink-muted">
                      <span className="h-1 w-1 rounded-full bg-brand-gradient" />
                      {theme}: {ids.length} paper{ids.length === 1 ? "" : "s"}
                    </li>
                  ))}
                </ul>
              </Section>
            )}

            {review.gaps && review.gaps.length > 0 && (
              <Section label="Gaps">
                <ul className="space-y-1">
                  {review.gaps.map((g, gi) => (
                    <li key={gi} className="flex gap-2 text-sm text-ink-muted">
                      <span className="mt-1.5 h-1 w-1 shrink-0 rounded-full bg-amber-400" />
                      {g}
                    </li>
                  ))}
                </ul>
              </Section>
            )}

            {review.outline && Object.keys(review.outline).length > 0 && (
              <Section label="Suggested outline">
                {Object.entries(review.outline).map(([section, bullets]) => (
                  <div key={section} className="mb-3 last:mb-0">
                    <p className="text-sm font-medium text-ink">{section}</p>
                    <ul className="mt-1 space-y-1">
                      {bullets.map((b, bi) => (
                        <li key={bi} className="flex gap-2 text-sm text-ink-muted">
                          <span className="mt-1.5 h-1 w-1 shrink-0 rounded-full bg-brand-gradient" />
                          {b}
                        </li>
                      ))}
                    </ul>
                  </div>
                ))}
              </Section>
            )}

            {review.suggested_reading && review.suggested_reading.length > 0 && (
              <Section label="Suggested reading">
                <ul className="space-y-1">
                  {review.suggested_reading.map((s, si) => (
                    <li key={si} className="flex gap-2 text-sm text-ink-muted">
                      <span className="mt-1.5 h-1 w-1 shrink-0 rounded-full bg-cyan-400" />
                      {s}
                    </li>
                  ))}
                </ul>
              </Section>
            )}
          </motion.div>
        ))}
      </div>
    </div>
  );
}

function Section({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div className="mb-4 last:mb-0">
      <h3 className="mb-1.5 text-xs font-semibold uppercase tracking-wide text-ink-faint">{label}</h3>
      {children}
    </div>
  );
}
