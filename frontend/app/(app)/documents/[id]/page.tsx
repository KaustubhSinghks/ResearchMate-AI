"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { motion, AnimatePresence } from "framer-motion";
import {
  MessageSquare,
  Network,
  GitCompare,
  Sparkles,
  ListTree,
  Database,
  StickyNote,
  Quote,
  Trash2,
  Plus,
  AlertCircle,
  Loader2,
} from "lucide-react";
import { api } from "@/lib/api";
import { CitationFormats, DocumentDetail, Note } from "@/lib/types";
import StatusBadge from "@/components/StatusBadge";
import Skeleton from "@/components/Skeleton";

const TABS = [
  { key: "Overview", icon: Sparkles },
  { key: "Sections", icon: ListTree },
  { key: "Metadata", icon: Database },
  { key: "Notes", icon: StickyNote },
  { key: "Citation", icon: Quote },
] as const;
type Tab = (typeof TABS)[number]["key"];

export default function DocumentDetailPage() {
  const params = useParams<{ id: string }>();
  const documentId = Number(params.id);
  const router = useRouter();

  const [doc, setDoc] = useState<DocumentDetail | null>(null);
  const [tab, setTab] = useState<Tab>("Overview");

  useEffect(() => {
    api.get<DocumentDetail>(`/documents/${documentId}`).then(setDoc);
  }, [documentId]);

  if (!doc) {
    return (
      <div className="space-y-3">
        <Skeleton className="h-8 w-2/3" />
        <Skeleton className="h-4 w-1/3" />
        <Skeleton className="h-40" />
      </div>
    );
  }

  return (
    <div>
      <motion.div initial={{ opacity: 0, y: -6 }} animate={{ opacity: 1, y: 0 }} className="mb-2 flex items-center gap-3">
        <h1 className="text-2xl font-semibold tracking-tight text-ink">{doc.title}</h1>
        <StatusBadge status={doc.status} />
      </motion.div>
      <p className="mb-6 text-sm text-ink-muted">
        {doc.venue ?? "Unknown venue"} {doc.year ? `· ${doc.year}` : ""}
      </p>

      <div className="mb-6 flex flex-wrap gap-3">
        <Link href={`/documents/${documentId}/chat`} className="btn-primary">
          <MessageSquare className="h-4 w-4" /> Chat with this paper
        </Link>
        <Link href={`/documents/${documentId}/related`} className="btn-secondary">
          <Network className="h-4 w-4" /> Find related papers
        </Link>
        <button onClick={() => router.push(`/compare?ids=${documentId}`)} className="btn-secondary">
          <GitCompare className="h-4 w-4" /> Compare
        </button>
      </div>

      {doc.status === "failed" && (
        <div className="mb-6 flex items-start gap-2 rounded-xl bg-red-500/10 p-3 text-sm text-red-500">
          <AlertCircle className="mt-0.5 h-4 w-4 shrink-0" />
          Processing failed: {doc.error_message}
        </div>
      )}
      {doc.status === "processing" && (
        <div className="mb-6 flex items-center gap-2 rounded-xl bg-amber-500/10 p-3 text-sm text-amber-500">
          <Loader2 className="h-4 w-4 shrink-0 animate-spin" />
          Still processing — summary and metadata will appear once ingestion finishes.
        </div>
      )}

      <div className="mb-6 flex gap-1 border-b border-border">
        {TABS.map(({ key, icon: Icon }) => (
          <button
            key={key}
            onClick={() => setTab(key)}
            className={`relative flex items-center gap-1.5 px-3 py-2.5 text-sm font-medium transition-colors ${
              tab === key ? "text-brand-500" : "text-ink-muted hover:text-ink"
            }`}
          >
            <Icon className="h-3.5 w-3.5" />
            {key}
            {tab === key && (
              <motion.div
                layoutId="doc-tab-underline"
                className="absolute -bottom-px left-0 right-0 h-0.5 rounded-full bg-brand-gradient"
                transition={{ type: "spring", stiffness: 400, damping: 32 }}
              />
            )}
          </button>
        ))}
      </div>

      <AnimatePresence mode="wait">
        <motion.div
          key={tab}
          initial={{ opacity: 0, y: 6 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.2 }}
        >
          {tab === "Overview" && <OverviewTab doc={doc} />}
          {tab === "Sections" && <SectionsTab doc={doc} />}
          {tab === "Metadata" && <MetadataTab doc={doc} />}
          {tab === "Notes" && <NotesTab documentId={documentId} />}
          {tab === "Citation" && <CitationTab documentId={documentId} />}
        </motion.div>
      </AnimatePresence>
    </div>
  );
}

function Field({ label, value }: { label: string; value: string | null }) {
  if (!value) return null;
  return (
    <div className="card mb-4 p-4">
      <h3 className="mb-1.5 text-xs font-semibold uppercase tracking-wide text-ink-faint">{label}</h3>
      <p className="text-sm leading-relaxed text-ink-muted">{value}</p>
    </div>
  );
}

function OverviewTab({ doc }: { doc: DocumentDetail }) {
  return (
    <div>
      <Field label="Short summary" value={doc.short_summary} />
      {doc.key_contributions && doc.key_contributions.length > 0 && (
        <div className="card mb-4 p-4">
          <h3 className="mb-2 text-xs font-semibold uppercase tracking-wide text-ink-faint">Key contributions</h3>
          <ul className="space-y-1.5">
            {doc.key_contributions.map((c, i) => (
              <li key={i} className="flex gap-2 text-sm text-ink-muted">
                <span className="mt-1.5 h-1 w-1 shrink-0 rounded-full bg-brand-gradient" />
                {c}
              </li>
            ))}
          </ul>
        </div>
      )}
      <Field label="Problem statement" value={doc.problem_statement} />
      <Field label="Methodology" value={doc.methodology} />
      <Field label="Results" value={doc.results} />
      <Field label="Limitations" value={doc.limitations} />
      <Field label="Conclusions" value={doc.conclusions} />
      <Field label="Future work" value={doc.future_work} />
      <Field label="Abstract" value={doc.abstract} />
    </div>
  );
}

function SectionsTab({ doc }: { doc: DocumentDetail }) {
  const entries = Object.entries(doc.section_summaries ?? {});
  if (entries.length === 0) return <p className="text-ink-muted">No section summaries yet.</p>;
  return (
    <div>
      {entries.map(([section, summary]) => (
        <Field key={section} label={section} value={summary} />
      ))}
    </div>
  );
}

function MetadataTab({ doc }: { doc: DocumentDetail }) {
  const lists: [string, string[] | null][] = [
    ["Keywords", doc.keywords],
    ["Datasets", doc.datasets],
    ["Models used", doc.models_used],
    ["Algorithms", doc.algorithms],
    ["Metrics", doc.metrics],
  ];
  const nonEmpty = lists.filter(([, items]) => items && items.length > 0);
  if (nonEmpty.length === 0) return <p className="text-ink-muted">No structured metadata yet.</p>;
  return (
    <div className="card p-4">
      {nonEmpty.map(([label, items]) => (
        <div key={label} className="mb-4 last:mb-0">
          <h3 className="mb-2 text-xs font-semibold uppercase tracking-wide text-ink-faint">{label}</h3>
          <div className="flex flex-wrap gap-1.5">
            {items!.map((item) => (
              <span
                key={item}
                className="rounded-full bg-brand-gradient-soft px-2.5 py-1 text-xs font-medium text-brand-500"
              >
                {item}
              </span>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}

function NotesTab({ documentId }: { documentId: number }) {
  const [notes, setNotes] = useState<Note[]>([]);
  const [content, setContent] = useState("");
  const [type, setType] = useState<Note["type"]>("note");

  function load() {
    api.get<Note[]>(`/documents/${documentId}/notes`).then(setNotes);
  }

  useEffect(load, [documentId]);

  async function addNote(e: React.FormEvent) {
    e.preventDefault();
    if (!content.trim()) return;
    await api.post("/notes", { document_id: documentId, content, type });
    setContent("");
    load();
  }

  async function toggleDone(note: Note) {
    await api.patch(`/notes/${note.id}`, { is_done: !note.is_done });
    load();
  }

  async function remove(noteId: number) {
    await api.delete(`/notes/${noteId}`);
    load();
  }

  return (
    <div>
      <form onSubmit={addNote} className="mb-6 flex gap-2">
        <select
          value={type}
          onChange={(e) => setType(e.target.value as Note["type"])}
          className="input-field w-32"
        >
          <option value="note">Note</option>
          <option value="highlight">Highlight</option>
          <option value="todo">Todo</option>
        </select>
        <input
          value={content}
          onChange={(e) => setContent(e.target.value)}
          placeholder="Add a note..."
          className="input-field flex-1"
        />
        <button type="submit" className="btn-primary">
          <Plus className="h-4 w-4" /> Add
        </button>
      </form>

      {notes.length === 0 ? (
        <p className="text-ink-muted">No notes yet.</p>
      ) : (
        <ul className="space-y-2">
          <AnimatePresence>
            {notes.map((note) => (
              <motion.li
                key={note.id}
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: "auto" }}
                exit={{ opacity: 0, height: 0 }}
                className="card flex items-start justify-between gap-3 p-3"
              >
                <div>
                  <span className="mr-2 rounded-full bg-brand-gradient-soft px-2 py-0.5 text-xs font-medium text-brand-500">
                    {note.type}
                  </span>
                  <span className={`text-sm ${note.is_done ? "text-ink-faint line-through" : "text-ink-muted"}`}>
                    {note.content}
                  </span>
                </div>
                <div className="flex shrink-0 gap-3 text-xs">
                  {note.type === "todo" && (
                    <button onClick={() => toggleDone(note)} className="text-brand-500 hover:text-brand-400">
                      {note.is_done ? "Undo" : "Done"}
                    </button>
                  )}
                  <button onClick={() => remove(note.id)} className="text-ink-faint hover:text-red-500">
                    <Trash2 className="h-3.5 w-3.5" />
                  </button>
                </div>
              </motion.li>
            ))}
          </AnimatePresence>
        </ul>
      )}
    </div>
  );
}

function CitationTab({ documentId }: { documentId: number }) {
  const [citation, setCitation] = useState<CitationFormats | null>(null);

  useEffect(() => {
    api.get<CitationFormats>(`/documents/${documentId}/citation`).then(setCitation);
  }, [documentId]);

  if (!citation) return <Skeleton className="h-40" />;

  return (
    <div className="space-y-4">
      {(["apa", "ieee", "acm"] as const).map((style) => (
        <div key={style} className="card p-4">
          <h3 className="mb-1.5 text-xs font-semibold uppercase tracking-wide text-ink-faint">{style}</h3>
          <p className="text-sm text-ink-muted">{citation[style]}</p>
        </div>
      ))}
      {(["bibtex", "ris"] as const).map((style) => (
        <div key={style} className="card p-4">
          <h3 className="mb-1.5 text-xs font-semibold uppercase tracking-wide text-ink-faint">{style}</h3>
          <pre className="overflow-x-auto text-xs text-ink-muted">{citation[style]}</pre>
        </div>
      ))}
    </div>
  );
}
