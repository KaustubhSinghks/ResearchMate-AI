"use client";

import { Suspense, useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import { GitCompare, Loader2 } from "lucide-react";
import { api } from "@/lib/api";
import { CompareResult, DocumentListItem } from "@/lib/types";
import PageHeader from "@/components/PageHeader";

export default function ComparePage() {
  return (
    <Suspense fallback={<p className="text-ink-muted">Loading...</p>}>
      <ComparePageInner />
    </Suspense>
  );
}

function ComparePageInner() {
  const searchParams = useSearchParams();
  const [documents, setDocuments] = useState<DocumentListItem[]>([]);
  const [selected, setSelected] = useState<Set<number>>(new Set());
  const [result, setResult] = useState<CompareResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.get<DocumentListItem[]>("/documents").then(setDocuments);
    const preset = searchParams.get("ids");
    if (preset) {
      setSelected(new Set(preset.split(",").map(Number)));
    }
  }, [searchParams]);

  function toggle(id: number) {
    setSelected((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  }

  async function runCompare() {
    setError(null);
    if (selected.size < 2) {
      setError("Select at least 2 documents.");
      return;
    }
    setLoading(true);
    try {
      const res = await api.post<CompareResult>("/compare", { document_ids: Array.from(selected) });
      setResult(res);
    } catch {
      setError("Comparison failed. Make sure the selected papers have finished processing.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div>
      <PageHeader title="Compare papers" description="Select two or more papers to compare side by side" />

      <div className="mb-6 grid grid-cols-2 gap-2">
        {documents.map((doc, i) => {
          const checked = selected.has(doc.id);
          return (
            <motion.label
              key={doc.id}
              initial={{ opacity: 0, y: 6 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: Math.min(i * 0.02, 0.3) }}
              className={`card flex cursor-pointer items-center gap-2.5 p-3 text-sm transition-colors ${
                checked ? "border-brand-400/60 bg-brand-gradient-soft" : ""
              }`}
            >
              <input type="checkbox" checked={checked} onChange={() => toggle(doc.id)} className="accent-brand-500" />
              <span className="text-ink">{doc.title}</span>
            </motion.label>
          );
        })}
      </div>

      <AnimatePresence>
        {error && (
          <motion.p
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            className="mb-4 rounded-lg bg-red-500/10 px-3 py-2 text-sm text-red-500"
          >
            {error}
          </motion.p>
        )}
      </AnimatePresence>

      <button onClick={runCompare} disabled={loading} className="btn-primary mb-8">
        {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <GitCompare className="h-4 w-4" />}
        {loading ? "Comparing..." : "Compare selected"}
      </button>

      {result && (
        <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }}>
          <p className="card mb-4 p-4 text-sm text-ink-muted">{result.narrative_summary}</p>
          <div className="card overflow-x-auto p-2">
            <table className="w-full min-w-[900px] border-collapse text-sm">
              <thead>
                <tr className="text-left text-xs uppercase tracking-wide text-ink-faint">
                  <th className="p-3">Paper</th>
                  <th className="p-3">Problem</th>
                  <th className="p-3">Method</th>
                  <th className="p-3">Dataset</th>
                  <th className="p-3">Performance</th>
                  <th className="p-3">Strengths</th>
                  <th className="p-3">Weaknesses</th>
                  <th className="p-3">Novelty</th>
                </tr>
              </thead>
              <tbody>
                {result.rows.map((row) => (
                  <tr key={row.document_id} className="border-t border-border align-top text-ink-muted">
                    <td className="p-3 font-medium text-ink">{row.title}</td>
                    <td className="p-3">{row.problem_addressed}</td>
                    <td className="p-3">{row.method_used}</td>
                    <td className="p-3">{row.dataset_or_benchmark}</td>
                    <td className="p-3">{row.performance}</td>
                    <td className="p-3">{row.strengths}</td>
                    <td className="p-3">{row.weaknesses}</td>
                    <td className="p-3">{row.novelty}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </motion.div>
      )}
    </div>
  );
}
