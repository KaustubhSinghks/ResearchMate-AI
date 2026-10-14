"""Times each stage of the ingestion pipeline and RAG chat latency against real APIs.

Ingestion stages run in-process (needs GEMINI_API_KEY / VOYAGE_API_KEY in the environment).
The chat benchmark hits a live backend over HTTP (needs the API server running).

Usage:
    cd backend && python scripts/benchmark_pipeline.py
"""

import json
import os
import statistics
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import fitz
import httpx

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.services.chunking import chunk_document
from app.services.embeddings import embed_documents
from app.services.metadata_extraction import extract_metadata
from app.services.pdf_extraction import extract_pdf
from app.services.summarization import summarize_paper

API_BASE = "http://localhost:8000"
RESULTS_DIR = Path(__file__).resolve().parent.parent / "benchmark_results"

SECTION_NAMES = [
    "Abstract",
    "Introduction",
    "Related Work",
    "Methodology",
    "Experiments",
    "Results",
    "Discussion",
    "Conclusion",
]
FILLER_SENTENCE = (
    "This section discusses relevant background, methodology details, and empirical "
    "findings related to the proposed approach, covering datasets, baselines, and "
    "evaluation metrics used to validate the claims made throughout the paper. "
)


def make_sample_pdf(path: Path, sections: int, repeats_per_section: int) -> None:
    doc = fitz.open()
    lines = ["Benchmark Paper on Neural Retrieval Methods", "Ada Researcher, Grace Scientist", ""]
    for name in SECTION_NAMES[:sections]:
        lines.append(name)
        lines.append(FILLER_SENTENCE * repeats_per_section)
        lines.append("")
    text = "\n".join(lines)

    page = doc.new_page()
    y = 72
    for line in text.split("\n"):
        if y > 780:
            page = doc.new_page()
            y = 72
        page.insert_text((50, y), line, fontsize=9)
        y += 12 * (1 + len(line) // 110)
    doc.save(str(path))
    doc.close()


def time_stage(fn, *args, **kwargs):
    start = time.perf_counter()
    result = fn(*args, **kwargs)
    return result, time.perf_counter() - start


def time_stage_with_retry(fn, *args, max_retries=3, backoff_sec=65, **kwargs):
    """Like time_stage, but retries on rate-limit errors. Backoff time is excluded
    from the reported duration since it reflects free-tier quota, not processing cost."""
    retries = 0
    for attempt in range(max_retries + 1):
        start = time.perf_counter()
        try:
            result = fn(*args, **kwargs)
            return result, time.perf_counter() - start, retries
        except Exception as exc:  # noqa: BLE001 - only retry rate limits, re-raise everything else
            is_rate_limit = "RESOURCE_EXHAUSTED" in str(exc) or "429" in str(exc)
            if not is_rate_limit or attempt == max_retries:
                raise
            retries += 1
            print(f"    rate limited, waiting {backoff_sec}s before retry {retries}/{max_retries}...")
            time.sleep(backoff_sec)


def benchmark_ingestion(pdf_path: Path, label: str) -> dict:
    timings = {}
    retries = {}
    extracted, timings["pdf_extraction"] = time_stage(extract_pdf, str(pdf_path))
    chunks, timings["chunking"] = time_stage(chunk_document, extracted)
    _, timings["embedding"] = time_stage(embed_documents, [c.text for c in chunks])
    _, timings["metadata_extraction"], retries["metadata_extraction"] = time_stage_with_retry(
        extract_metadata, extracted.full_text, extracted.title_guess
    )
    _, timings["summarization"], retries["summarization"] = time_stage_with_retry(
        summarize_paper, extracted.full_text, [s.name for s in extracted.sections]
    )
    timings["total"] = sum(timings.values())
    return {
        "label": label,
        "page_count": extracted.page_count,
        "chunk_count": len(chunks),
        "timings_sec": {k: round(v, 3) for k, v in timings.items()},
        "rate_limit_retries": {k: v for k, v in retries.items() if v > 0},
    }


def login(client: httpx.Client, email: str, password: str) -> str:
    resp = client.post("/auth/login", data={"username": email, "password": password})
    if resp.status_code == 401:
        client.post("/auth/signup", json={"email": email, "password": password})
        resp = client.post("/auth/login", data={"username": email, "password": password})
    resp.raise_for_status()
    return resp.json()["access_token"]


def benchmark_chat(client: httpx.Client, document_id: int, questions: list[str], max_retries=2, backoff_sec=65) -> dict:
    latencies = []
    for q in questions:
        for attempt in range(max_retries + 1):
            start = time.perf_counter()
            resp = client.post("/chat", json={"question": q, "document_id": document_id})
            if resp.status_code == 500 and attempt < max_retries:
                print(f"    chat call failed (likely rate limit), waiting {backoff_sec}s before retry...")
                time.sleep(backoff_sec)
                continue
            resp.raise_for_status()
            latencies.append(time.perf_counter() - start)
            break

    sorted_lat = sorted(latencies)
    p95_index = max(0, int(len(sorted_lat) * 0.95) - 1)
    return {
        "count": len(latencies),
        "min_sec": round(min(latencies), 3),
        "max_sec": round(max(latencies), 3),
        "mean_sec": round(statistics.mean(latencies), 3),
        "p95_sec": round(sorted_lat[p95_index], 3),
        "all_sec": [round(x, 3) for x in latencies],
    }


def print_ingestion_table(results: list[dict]) -> None:
    stages = ["pdf_extraction", "chunking", "embedding", "metadata_extraction", "summarization", "total"]
    header = f"{'Paper':<10}{'Pages':<7}{'Chunks':<8}" + "".join(f"{s:<20}" for s in stages)
    print(header)
    print("-" * len(header))
    for r in results:
        row = f"{r['label']:<10}{r['page_count']:<7}{r['chunk_count']:<8}"
        row += "".join(f"{r['timings_sec'][s]:<20.3f}" for s in stages)
        print(row)


def main() -> None:
    tmp_dir = Path("/tmp/benchmark_pdfs")
    tmp_dir.mkdir(exist_ok=True)

    sizes = [
        ("small", 2, 2),
        ("medium", 5, 4),
        ("large", 8, 8),
    ]

    print("=== Ingestion pipeline benchmark ===\n")
    ingestion_results = []
    for label, sections, repeats in sizes:
        pdf_path = tmp_dir / f"{label}.pdf"
        make_sample_pdf(pdf_path, sections, repeats)
        print(f"Running {label} paper ({sections} sections)...")
        result = benchmark_ingestion(pdf_path, label)
        ingestion_results.append(result)
    print()
    print_ingestion_table(ingestion_results)

    print("\n=== RAG chat latency benchmark ===\n")
    chat_result = None
    try:
        with httpx.Client(base_url=API_BASE, timeout=60) as client:
            email = os.environ.get("BENCHMARK_EMAIL", "gemini-test@example.com")
            password = os.environ.get("BENCHMARK_PASSWORD", "testpass123")
            token = login(client, email, password)
            client.headers["Authorization"] = f"Bearer {token}"

            docs = client.get("/documents").json()
            ready_docs = [d for d in docs if d["status"] == "ready"]
            if not ready_docs:
                print("No 'ready' documents found in the running backend — skipping chat benchmark.")
                print("(Upload and wait for a paper to finish processing first.)")
            else:
                document_id = ready_docs[0]["id"]
                print(f"Using document #{document_id}: {ready_docs[0]['title']}\n")
                questions = [
                    "What problem does this paper address?",
                    "What method or approach is used?",
                    "What were the main results?",
                    "What are the limitations mentioned?",
                    "Summarize the conclusion in one sentence.",
                ]
                chat_result = benchmark_chat(client, document_id, questions)
                print(f"{'count':<8}{'min':<8}{'mean':<8}{'p95':<8}{'max':<8}")
                print(
                    f"{chat_result['count']:<8}{chat_result['min_sec']:<8}"
                    f"{chat_result['mean_sec']:<8}{chat_result['p95_sec']:<8}{chat_result['max_sec']:<8}"
                )
    except httpx.ConnectError:
        print(f"Could not reach backend at {API_BASE} — skipping chat benchmark.")

    RESULTS_DIR.mkdir(exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_path = RESULTS_DIR / f"{timestamp}.json"
    out_path.write_text(
        json.dumps({"timestamp": timestamp, "ingestion": ingestion_results, "chat": chat_result}, indent=2)
    )
    print(f"\nSaved full results to {out_path}")


if __name__ == "__main__":
    main()
