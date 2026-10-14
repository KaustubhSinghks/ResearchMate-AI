"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import { FileText, CheckCircle2, Loader2, XCircle, Upload as UploadIcon } from "lucide-react";
import { api } from "@/lib/api";
import { DocumentListItem } from "@/lib/types";
import DocumentCard from "@/components/DocumentCard";
import StatTile from "@/components/StatTile";
import PageHeader from "@/components/PageHeader";
import Skeleton from "@/components/Skeleton";

export default function DashboardPage() {
  const [documents, setDocuments] = useState<DocumentListItem[] | null>(null);

  useEffect(() => {
    api.get<DocumentListItem[]>("/documents").then(setDocuments).catch(() => setDocuments([]));
  }, []);

  const ready = documents?.filter((d) => d.status === "ready").length ?? 0;
  const processing = documents?.filter((d) => d.status === "processing").length ?? 0;
  const failed = documents?.filter((d) => d.status === "failed").length ?? 0;

  return (
    <div>
      <PageHeader
        title="Dashboard"
        description="Your research library at a glance"
        actions={
          <Link href="/upload" className="btn-primary">
            <UploadIcon className="h-4 w-4" /> Upload
          </Link>
        }
      />

      <div className="mb-8 grid grid-cols-2 gap-4 sm:grid-cols-4">
        <StatTile label="Total papers" value={documents?.length ?? "-"} icon={FileText} accent="brand" delay={0} />
        <StatTile label="Ready" value={ready} icon={CheckCircle2} accent="emerald" delay={0.05} />
        <StatTile label="Processing" value={processing} icon={Loader2} accent="amber" delay={0.1} />
        <StatTile label="Failed" value={failed} icon={XCircle} accent="red" delay={0.15} />
      </div>

      <div className="mb-4 flex items-center justify-between">
        <h2 className="text-lg font-medium text-ink">Recent papers</h2>
        <Link href="/documents" className="text-sm text-brand-500 hover:text-brand-400">
          View all
        </Link>
      </div>

      {documents === null ? (
        <div className="grid grid-cols-2 gap-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <Skeleton key={i} className="h-24" />
          ))}
        </div>
      ) : documents.length === 0 ? (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="card flex flex-col items-center justify-center gap-3 p-12 text-center"
        >
          <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-brand-gradient-soft text-brand-500">
            <FileText className="h-6 w-6" />
          </div>
          <p className="text-ink-muted">No papers yet.</p>
          <Link href="/upload" className="btn-primary">
            <UploadIcon className="h-4 w-4" /> Upload your first paper
          </Link>
        </motion.div>
      ) : (
        <div className="grid grid-cols-2 gap-4">
          {documents.slice(0, 8).map((doc, i) => (
            <DocumentCard key={doc.id} doc={doc} index={i} />
          ))}
        </div>
      )}
    </div>
  );
}
