import { CheckCircle2, Loader2, XCircle } from "lucide-react";
import { DocumentStatus } from "@/lib/types";

const CONFIG: Record<DocumentStatus, { classes: string; icon: typeof CheckCircle2; spin?: boolean }> = {
  processing: { classes: "bg-amber-500/10 text-amber-500", icon: Loader2, spin: true },
  ready: { classes: "bg-emerald-500/10 text-emerald-500", icon: CheckCircle2 },
  failed: { classes: "bg-red-500/10 text-red-500", icon: XCircle },
};

export default function StatusBadge({ status }: { status: DocumentStatus }) {
  const { classes, icon: Icon, spin } = CONFIG[status];
  return (
    <span className={`inline-flex items-center gap-1 rounded-full px-2.5 py-1 text-xs font-medium ${classes}`}>
      <Icon className={`h-3 w-3 ${spin ? "animate-spin" : ""}`} />
      {status}
    </span>
  );
}
