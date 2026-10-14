"use client";

import { useEffect, useMemo, useState } from "react";
import { Search } from "lucide-react";
import { api } from "@/lib/api";
import { DocumentListItem } from "@/lib/types";
import DocumentCard from "@/components/DocumentCard";
import PageHeader from "@/components/PageHeader";
import Skeleton from "@/components/Skeleton";

export default function DocumentsPage() {
  const [documents, setDocuments] = useState<DocumentListItem[] | null>(null);
  const [filter, setFilter] = useState("");

  useEffect(() => {
    api.get<DocumentListItem[]>("/documents").then(setDocuments);
  }, []);

  const filtered = useMemo(() => {
    const q = filter.trim().toLowerCase();
    if (!documents) return [];
    if (!q) return documents;
    return documents.filter(
      (d) => d.title.toLowerCase().includes(q) || (d.venue ?? "").toLowerCase().includes(q)
    );
  }, [documents, filter]);

  return (
    <div>
      <PageHeader title="Documents" description="Everything in your research library" />

      <div className="relative mb-6 max-w-sm">
        <Search className="pointer-events-none absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-ink-faint" />
        <input
          placeholder="Filter by title or venue..."
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
          className="input-field pl-10"
        />
      </div>

      {documents === null ? (
        <div className="grid grid-cols-2 gap-4">
          {Array.from({ length: 6 }).map((_, i) => (
            <Skeleton key={i} className="h-24" />
          ))}
        </div>
      ) : filtered.length === 0 ? (
        <p className="text-ink-muted">No documents match.</p>
      ) : (
        <div className="grid grid-cols-2 gap-4">
          {filtered.map((doc, i) => (
            <DocumentCard key={doc.id} doc={doc} index={i} />
          ))}
        </div>
      )}
    </div>
  );
}
