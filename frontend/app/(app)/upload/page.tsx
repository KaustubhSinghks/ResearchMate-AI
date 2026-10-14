"use client";

import { useCallback, useEffect, useState } from "react";
import { useDropzone } from "react-dropzone";
import { motion, AnimatePresence } from "framer-motion";
import { UploadCloud, FileUp, Loader2 } from "lucide-react";
import { api, ApiError } from "@/lib/api";
import { DocumentListItem } from "@/lib/types";
import DocumentCard from "@/components/DocumentCard";
import PageHeader from "@/components/PageHeader";

export default function UploadPage() {
  const [uploaded, setUploaded] = useState<DocumentListItem[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [uploading, setUploading] = useState(false);

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    setError(null);
    setUploading(true);
    try {
      for (const file of acceptedFiles) {
        const formData = new FormData();
        formData.append("file", file);
        const doc = await api.upload<DocumentListItem>("/documents/upload", formData);
        setUploaded((prev) => [doc, ...prev]);
      }
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Upload failed");
    } finally {
      setUploading(false);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { "application/pdf": [".pdf"] },
  });

  useEffect(() => {
    const processingIds = uploaded.filter((d) => d.status === "processing").map((d) => d.id);
    if (processingIds.length === 0) return;

    const interval = setInterval(async () => {
      const updates = await Promise.all(processingIds.map((id) => api.get<DocumentListItem>(`/documents/${id}`)));
      setUploaded((prev) =>
        prev.map((doc) => updates.find((u) => u.id === doc.id) as DocumentListItem ?? doc)
      );
    }, 4000);

    return () => clearInterval(interval);
  }, [uploaded]);

  return (
    <div>
      <PageHeader title="Upload papers" description="Drop in PDFs to extract, summarize, and index them" />

      <div
        {...getRootProps()}
        className={`card mb-8 flex h-48 scale-100 cursor-pointer flex-col items-center justify-center gap-3 border-2 border-dashed text-sm transition-transform duration-200 ${
          isDragActive ? "scale-[1.01] border-brand-400" : ""
        }`}
      >
        <input {...getInputProps()} />
        <motion.div
          animate={{ y: isDragActive ? -4 : 0 }}
          className="flex h-12 w-12 items-center justify-center rounded-xl bg-brand-gradient-soft text-brand-500"
        >
          {uploading ? (
            <Loader2 className="h-6 w-6 animate-spin" />
          ) : isDragActive ? (
            <FileUp className="h-6 w-6" />
          ) : (
            <UploadCloud className="h-6 w-6" />
          )}
        </motion.div>
        <p className="text-ink-muted">
          {uploading ? "Uploading..." : isDragActive ? "Drop PDFs here" : "Drag & drop PDFs here, or click to select"}
        </p>
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

      {uploaded.length > 0 && (
        <div className="grid grid-cols-2 gap-4">
          {uploaded.map((doc, i) => (
            <DocumentCard key={doc.id} doc={doc} index={i} />
          ))}
        </div>
      )}
    </div>
  );
}
