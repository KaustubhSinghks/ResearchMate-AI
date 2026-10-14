"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { motion, AnimatePresence } from "framer-motion";
import { StickyNote, Trash2, FileText } from "lucide-react";
import { api } from "@/lib/api";
import { Note } from "@/lib/types";
import PageHeader from "@/components/PageHeader";
import Skeleton from "@/components/Skeleton";

export default function NotesPage() {
  const [notes, setNotes] = useState<Note[] | null>(null);

  function load() {
    api.get<Note[]>("/notes").then(setNotes);
  }

  useEffect(load, []);

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
      <PageHeader title="Notes" description="Highlights, notes, and TODOs across your library" />

      {notes === null ? (
        <div className="space-y-2">
          {Array.from({ length: 3 }).map((_, i) => (
            <Skeleton key={i} className="h-16" />
          ))}
        </div>
      ) : notes.length === 0 ? (
        <div className="card flex flex-col items-center gap-3 p-12 text-center">
          <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-brand-gradient-soft text-brand-500">
            <StickyNote className="h-6 w-6" />
          </div>
          <p className="text-ink-muted">
            No notes yet. Add notes, highlights, and TODOs from a paper&apos;s detail page.
          </p>
        </div>
      ) : (
        <ul className="space-y-2">
          <AnimatePresence>
            {notes.map((note) => (
              <motion.li
                key={note.id}
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: "auto" }}
                exit={{ opacity: 0, height: 0 }}
                className="card flex items-start justify-between gap-3 p-4"
              >
                <div>
                  <span className="mr-2 rounded-full bg-brand-gradient-soft px-2 py-0.5 text-xs font-medium text-brand-500">
                    {note.type}
                  </span>
                  <span className={`text-sm ${note.is_done ? "text-ink-faint line-through" : "text-ink-muted"}`}>
                    {note.content}
                  </span>
                  <div className="mt-1.5">
                    <Link
                      href={`/documents/${note.document_id}`}
                      className="inline-flex items-center gap-1 text-xs text-brand-500 hover:text-brand-400"
                    >
                      <FileText className="h-3 w-3" /> View paper
                    </Link>
                  </div>
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
