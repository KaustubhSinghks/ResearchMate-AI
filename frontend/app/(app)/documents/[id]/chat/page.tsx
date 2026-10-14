"use client";

import { useState, useRef, useEffect } from "react";
import { useParams } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import { Send, Sparkles, User, Quote } from "lucide-react";
import { api } from "@/lib/api";
import { ChatResponse } from "@/lib/types";

interface Turn {
  question: string;
  response: ChatResponse;
}

export default function DocumentChatPage() {
  const params = useParams<{ id: string }>();
  const documentId = Number(params.id);

  const [question, setQuestion] = useState("");
  const [turns, setTurns] = useState<Turn[]>([]);
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [turns, loading]);

  async function ask(e: React.FormEvent) {
    e.preventDefault();
    if (!question.trim()) return;
    const q = question;
    setQuestion("");
    setLoading(true);
    try {
      const response = await api.post<ChatResponse>("/chat", { question: q, document_id: documentId });
      setTurns((prev) => [...prev, { question: q, response }]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="mx-auto flex h-[calc(100vh-8rem)] max-w-2xl flex-col">
      <motion.h1
        initial={{ opacity: 0, y: -6 }}
        animate={{ opacity: 1, y: 0 }}
        className="mb-6 text-2xl font-semibold tracking-tight text-ink"
      >
        Chat with this paper
      </motion.h1>

      <div className="flex-1 space-y-6 overflow-y-auto pb-4">
        {turns.length === 0 && !loading && (
          <div className="card flex flex-col items-center gap-2 p-8 text-center">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-brand-gradient-soft text-brand-500">
              <Sparkles className="h-5 w-5" />
            </div>
            <p className="text-sm text-ink-muted">
              Ask something like &ldquo;What problem does this paper solve?&rdquo; or &ldquo;What are the main
              results?&rdquo;
            </p>
          </div>
        )}

        <AnimatePresence initial={false}>
          {turns.map((turn, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3 }}
              className="space-y-3"
            >
              <div className="flex items-start gap-2.5">
                <div className="mt-0.5 flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-surface-raised text-ink-muted">
                  <User className="h-3.5 w-3.5" />
                </div>
                <p className="mt-1 text-sm font-medium text-ink">{turn.question}</p>
              </div>

              <div className="flex items-start gap-2.5">
                <div className="mt-0.5 flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-brand-gradient text-white">
                  <Sparkles className="h-3.5 w-3.5" />
                </div>
                <div className="flex-1 space-y-3">
                  <p className="card whitespace-pre-wrap p-3.5 text-sm leading-relaxed text-ink-muted">
                    {turn.response.answer}
                  </p>
                  {turn.response.citations.length > 0 && (
                    <div className="space-y-1.5">
                      {turn.response.citations.map((c, j) => (
                        <div
                          key={j}
                          className="flex items-start gap-2 rounded-lg bg-surface-raised px-3 py-2 text-xs text-ink-faint"
                        >
                          <Quote className="mt-0.5 h-3 w-3 shrink-0 text-brand-500" />
                          <span>
                            <span className="font-medium text-ink-muted">
                              [{j + 1}] {c.section ? `${c.section}, ` : ""}
                              {c.page ? `page ${c.page}: ` : ""}
                            </span>
                            {c.text.slice(0, 200)}...
                          </span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            </motion.div>
          ))}
        </AnimatePresence>

        {loading && (
          <div className="flex items-center gap-2.5">
            <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-brand-gradient text-white">
              <Sparkles className="h-3.5 w-3.5" />
            </div>
            <div className="flex gap-1">
              {[0, 1, 2].map((i) => (
                <motion.span
                  key={i}
                  className="h-2 w-2 rounded-full bg-brand-400"
                  animate={{ opacity: [0.3, 1, 0.3] }}
                  transition={{ duration: 1.2, repeat: Infinity, delay: i * 0.2 }}
                />
              ))}
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      <form onSubmit={ask} className="flex gap-2 border-t border-border pt-4">
        <input
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="Ask a question about this paper..."
          className="input-field flex-1"
        />
        <button type="submit" disabled={loading} className="btn-primary">
          <Send className="h-4 w-4" />
        </button>
      </form>
    </div>
  );
}
