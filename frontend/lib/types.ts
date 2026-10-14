export type DocumentStatus = "processing" | "ready" | "failed";

export interface DocumentListItem {
  id: number;
  title: string;
  year: number | null;
  venue: string | null;
  status: DocumentStatus;
  short_summary: string | null;
  created_at: string;
  folder_id: number | null;
}

export interface DocumentDetail {
  id: number;
  title: string;
  original_filename: string;
  year: number | null;
  venue: string | null;
  doi: string | null;
  abstract: string | null;
  keywords: string[] | null;
  datasets: string[] | null;
  models_used: string[] | null;
  algorithms: string[] | null;
  metrics: string[] | null;
  problem_statement: string | null;
  methodology: string | null;
  results: string | null;
  limitations: string | null;
  conclusions: string | null;
  future_work: string | null;
  short_summary: string | null;
  section_summaries: Record<string, string> | null;
  key_contributions: string[] | null;
  status: DocumentStatus;
  error_message: string | null;
  created_at: string;
}

export interface Folder {
  id: number;
  name: string;
  parent_id: number | null;
}

export interface Tag {
  id: number;
  name: string;
}

export interface CitedChunk {
  document_id: number;
  document_title: string;
  section: string | null;
  page: number | null;
  text: string;
}

export interface ChatResponse {
  answer: string;
  citations: CitedChunk[];
}

export interface SearchResult {
  document_id: number;
  title: string;
  year: number | null;
  venue: string | null;
  short_summary: string | null;
  matched_snippet: string | null;
  score: number;
  match_type: "keyword" | "semantic";
}

export interface RelatedPaper {
  relation: "cites" | "cited_by" | "similar" | "recommended";
  document_id: number | null;
  external_paper_id: string | null;
  title: string;
  authors: string[] | null;
  year: number | null;
  url: string | null;
  score: number | null;
}

export interface PaperComparisonRow {
  document_id: number;
  title: string;
  problem_addressed: string;
  method_used: string;
  dataset_or_benchmark: string;
  performance: string;
  strengths: string;
  weaknesses: string;
  novelty: string;
  practical_applications: string;
}

export interface CompareResult {
  rows: PaperComparisonRow[];
  narrative_summary: string;
}

export interface NoteType {
  type: "note" | "highlight" | "todo" | "summary";
}

export interface Note {
  id: number;
  document_id: number;
  type: "note" | "highlight" | "todo" | "summary";
  content: string;
  section_ref: string | null;
  is_done: boolean;
  created_at: string;
}

export interface GraphNode {
  id: string;
  label: string;
  type: "document" | "author" | "tag";
}

export interface GraphEdge {
  source: string;
  target: string;
  type: string;
  weight: number;
}

export interface GraphResponse {
  nodes: GraphNode[];
  edges: GraphEdge[];
}

export interface ReviewResult {
  id: number;
  title: string;
  document_ids: number[];
  themes: Record<string, number[]> | null;
  trends: Record<string, number> | null;
  gaps: string[] | null;
  outline: Record<string, string[]> | null;
  suggested_reading: string[] | null;
  created_at: string;
}

export interface CitationFormats {
  apa: string;
  ieee: string;
  acm: string;
  bibtex: string;
  ris: string;
}

export interface User {
  id: number;
  email: string;
  full_name: string | null;
  created_at: string;
}
