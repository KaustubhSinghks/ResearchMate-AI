"use client";

import { useEffect, useState } from "react";
import dynamic from "next/dynamic";
import { Network } from "lucide-react";
import { api } from "@/lib/api";
import { GraphResponse } from "@/lib/types";
import { useTheme } from "@/lib/theme";
import PageHeader from "@/components/PageHeader";
import Skeleton from "@/components/Skeleton";

const ForceGraph2D = dynamic(() => import("react-force-graph-2d"), { ssr: false });

const NODE_COLORS: Record<string, string> = {
  document: "#6366f1",
  author: "#06b6d4",
  tag: "#22c55e",
};

const LEGEND = [
  { label: "Document", color: NODE_COLORS.document },
  { label: "Author", color: NODE_COLORS.author },
  { label: "Tag", color: NODE_COLORS.tag },
];

export default function GraphPage() {
  const [graph, setGraph] = useState<GraphResponse | null>(null);
  const { theme } = useTheme();

  useEffect(() => {
    api.get<GraphResponse>("/graph").then(setGraph);
  }, []);

  return (
    <div>
      <PageHeader title="Knowledge graph" description="Papers connected to authors, tags, and each other" />

      <div className="mb-4 flex gap-4">
        {LEGEND.map((item) => (
          <div key={item.label} className="flex items-center gap-1.5 text-xs text-ink-muted">
            <span className="h-2.5 w-2.5 rounded-full" style={{ backgroundColor: item.color }} />
            {item.label}
          </div>
        ))}
      </div>

      {!graph ? (
        <Skeleton className="h-[70vh]" />
      ) : graph.nodes.length === 0 ? (
        <div className="card flex flex-col items-center gap-3 p-16 text-center">
          <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-brand-gradient-soft text-brand-500">
            <Network className="h-6 w-6" />
          </div>
          <p className="text-ink-muted">Upload and tag some papers to see the graph.</p>
        </div>
      ) : (
        <div className="card h-[70vh] w-full overflow-hidden">
          <ForceGraph2D
            graphData={{
              nodes: graph.nodes.map((n) => ({ ...n })),
              links: graph.edges.map((e) => ({ ...e })),
            }}
            nodeLabel="label"
            nodeColor={(n: any) => NODE_COLORS[n.type] ?? "#94a3b8"}
            nodeRelSize={5}
            linkColor={() => (theme === "dark" ? "rgba(148,163,184,0.25)" : "rgba(100,116,139,0.25)")}
            linkWidth={(l: any) => Math.min(l.weight ?? 1, 4)}
            backgroundColor="rgba(0,0,0,0)"
          />
        </div>
      )}
    </div>
  );
}
