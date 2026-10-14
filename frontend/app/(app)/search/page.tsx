"use client";

import { useState } from "react";
import Link from "next/link";
import { motion, AnimatePresence } from "framer-motion";
import { Search as SearchIcon, Loader2 } from "lucide-react";
import { api } from "@/lib/api";
import { SearchResult } from "@/lib/types";
import PageHeader from "@/components/PageHeader";

export default function SearchPage() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<SearchResult[] | null>(null);
  const [loading, setLoading] = useState(false);

  async function search(e: React.FormEvent) {
    e.preventDefault();
    if (!query.trim()) return;
    setLoading(true);
    try {
      const data = await api.get<SearchResult[]>(`/search?q=${encodeURIComponent(query)}`);
      setResults(data);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div>
      <PageHeader title="Search" description="Search by title, author, keyword, or topic" />

      <form onSubmit={search} className="mb-8 flex gap-2">
        <div className="relative flex-1">
          <SearchIcon className="pointer-events-none absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-ink-faint" />
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search across all uploaded papers..."
            className="input-field pl-10"
          />
        </div>
        <button type="submit" disabled={loading} className="btn-primary">
          {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <SearchIcon className="h-4 w-4" />}
          Search
        </button>
      </form>

      {results === null ? (
        <p className="text-ink-muted">Search across titles, abstracts, and paper content.</p>
      ) : results.length === 0 ? (
        <p className="text-ink-muted">No results.</p>
      ) : (
        <ul className="space-y-2">
          <AnimatePresence>
            {results.map((r, i) => (
              <motion.li
                key={r.document_id}
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: Math.min(i * 0.03, 0.3) }}
                className="card card-hover p-4"
              >
                <div className="flex items-center justify-between gap-2">
                  <Link href={`/documents/${r.document_id}`} className="font-medium text-ink hover:text-brand-500">
                    {r.title}
                  </Link>
                  <span
                    className={`shrink-0 rounded-full px-2 py-0.5 text-xs font-medium ${
                      r.match_type === "semantic" ? "bg-brand-gradient-soft text-brand-500" : "bg-cyan-500/10 text-cyan-500"
                    }`}
                  >
                    {r.match_type}
                  </span>
                </div>
                <p className="mt-0.5 text-xs text-ink-faint">
                  {r.venue ?? "Unknown venue"} {r.year ? `· ${r.year}` : ""}
                </p>
                {r.matched_snippet && <p className="mt-2 text-sm text-ink-muted">{r.matched_snippet}</p>}
              </motion.li>
            ))}
          </AnimatePresence>
        </ul>
      )}
    </div>
  );
}
