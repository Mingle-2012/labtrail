#!/usr/bin/env python3
"""End-to-end verification against the running LabTrail backend.

Requires:
  - PowerContext Server at POWERCONTEXT_URL (default http://127.0.0.1:8890)
  - FastAPI backend at http://127.0.0.1:8000

Writes evidence/verification.log and evidence/verification.json.
"""
from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EVIDENCE = ROOT / "evidence"
EVIDENCE.mkdir(exist_ok=True)

BASE_URL = os.getenv("LABTRAIL_URL", "http://127.0.0.1:8000").rstrip("/")
POWERCONTEXT_URL = os.getenv("POWERCONTEXT_URL", "http://127.0.0.1:8890").rstrip("/")
PROJECT_ID = "demo_project"
QUERY = "Why does OOD query distribution degrade graph index performance?"

checks: list[dict] = []
samples: dict = {}


def call(method: str, url: str, payload: dict | None = None, timeout: float = 60.0):
    data = None
    headers = {"Accept": "application/json"}
    if payload is not None:
        data = json.dumps(payload, ensure_ascii=False).encode()
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        body = resp.read().decode()
        return resp.status, json.loads(body) if body else None


def check(name: str, fn):
    started = time.perf_counter()
    try:
        detail = fn()
        elapsed = (time.perf_counter() - started) * 1000
        checks.append({"name": name, "ok": True, "detail": detail, "latency_ms": round(elapsed, 1)})
        print(f"[PASS] {name} ({elapsed:.0f} ms)\n       {detail}")
        return True
    except Exception as exc:  # noqa: BLE001 - report any failure
        elapsed = (time.perf_counter() - started) * 1000
        checks.append({"name": name, "ok": False, "detail": str(exc), "latency_ms": round(elapsed, 1)})
        print(f"[FAIL] {name} ({elapsed:.0f} ms)\n       {exc}")
        return False


def main() -> int:
    print(f"LabTrail verification @ {datetime.now().isoformat(timespec='seconds')}")
    print(f"backend={BASE_URL} powercontext={POWERCONTEXT_URL} project={PROJECT_ID}\n")

    def health():
        status, data = call("GET", f"{BASE_URL}/api/health")
        assert status == 200, status
        services = data.get("services", {})
        assert services.get("seekdb") == "connected", services
        assert services.get("powercontext") == "ready", services
        samples["health"] = data
        return f"seekdb={services['seekdb']}, powercontext={services['powercontext']}"

    def powercontext_direct():
        status, data = call("GET", f"{POWERCONTEXT_URL}/health/ready")
        assert status == 200, status
        status2, scopes = call("GET", f"{POWERCONTEXT_URL}/v1/scopes")
        assert status2 == 200, status2
        items = scopes.get("items") or scopes.get("scopes") or []
        titles = [s.get("title", "") for s in items]
        assert any(t.startswith("LabTrail") for t in titles), titles
        samples["powercontext_scopes"] = titles
        return f"ready, scopes={len(titles)} -> {', '.join(titles)}"

    def hybrid_search():
        status, data = call(
            "POST",
            f"{BASE_URL}/api/documents/search?project_id={PROJECT_ID}",
            {"query": QUERY, "mode": "hybrid", "n_results": 5},
        )
        assert status == 200, status
        results = data.get("results", [])
        assert results, data
        files = [r["metadata"].get("file_name", "") for r in results]
        assert any(f in ("ood_analysis_notes.md", "query_aware_construction.md") for f in files), files
        assert all("score" in r for r in results)
        samples["hybrid_search"] = [
            {
                "file": r["metadata"].get("file_name"),
                "page": r["metadata"].get("page"),
                "score": round(r["score"], 4),
                "text": r["text"][:160],
            }
            for r in results[:3]
        ]
        return f"{len(results)} results, top files={files[:3]}"

    def vector_search():
        status, data = call(
            "POST",
            f"{BASE_URL}/api/documents/search?project_id={PROJECT_ID}",
            {"query": QUERY, "mode": "vector", "n_results": 3},
        )
        assert status == 200, status
        results = data.get("results", [])
        assert results, data
        assert all(0.0 <= r["score"] <= 1.0 for r in results), results
        samples["vector_search"] = [
            {"file": r["metadata"].get("file_name"), "score": round(r["score"], 4)} for r in results
        ]
        return f"{len(results)} results (cosine similarity), top={results[0]['metadata'].get('file_name')}"

    def fulltext_search():
        status, data = call(
            "POST",
            f"{BASE_URL}/api/documents/search?project_id={PROJECT_ID}",
            {"query": "OOD query distribution", "mode": "fulltext", "n_results": 3},
        )
        assert status == 200, status
        results = data.get("results", [])
        assert results, data
        top_file = results[0]["metadata"].get("file_name")
        assert top_file == "ood_analysis_notes.md", [r["metadata"].get("file_name") for r in results]
        samples["fulltext_search"] = [
            {"file": r["metadata"].get("file_name"), "score": round(r["score"], 4)} for r in results
        ]
        return f"{len(results)} results (fulltext relevance), top={top_file}"

    def experiments():
        status, data = call("GET", f"{BASE_URL}/api/experiments/{PROJECT_ID}")
        assert status == 200, status
        assert data.get("total_records") == 30, data.get("total_records")
        assert set(data.get("methods", [])) == {"HNSW", "Vamana"}, data.get("methods")
        assert len(data.get("datasets", [])) == 4, data.get("datasets")
        recall = data["summary"]["Vamana"]["recall@10"]["mean"]
        samples["experiments"] = {
            "total_records": data["total_records"],
            "methods": data["methods"],
            "datasets": data["datasets"],
            "vamana_recall_mean": round(recall, 4),
        }
        return f"30 records, methods={data['methods']}, vamana recall mean={recall:.4f}"

    memory_text = f"Verification memory {int(time.time())}: prefer testing OOD recall before quantization."
    memory_id_holder = {"id": None, "scope_id": None}

    def memory_save():
        status, data = call(
            "POST",
            f"{BASE_URL}/api/memory",
            {
                "project_id": PROJECT_ID,
                "content": memory_text,
                "memory_type": "decision",
                "tags": ["verification", "OOD"],
            },
        )
        assert status == 200, status
        assert data.get("content") == memory_text, data
        memory_id_holder["id"] = data.get("id")
        memory_id_holder["scope_id"] = data.get("scope_id")
        assert memory_id_holder["id"], data
        samples["memory_save"] = {
            "id": data.get("id"),
            "scope_id": data.get("scope_id"),
            "memory_type": data.get("memory_type"),
        }
        return f"artifact={data['id']} scope={data.get('scope_id')}"

    def memory_search():
        status, data = call(
            "POST",
            f"{BASE_URL}/api/memory/search",
            {"project_id": PROJECT_ID, "query": "OOD recall verification", "n_results": 5},
        )
        assert status == 200, status
        results = data.get("results", [])
        assert results, data
        joined = " ".join(r.get("content", "") for r in results)
        assert "Verification memory" in joined, joined[:300]
        samples["memory_search"] = [
            {"score": round(r.get("score", 0), 3), "content": r.get("content", "")[:120]} for r in results[:3]
        ]
        return f"{len(results)} results, verification memory found"

    def memory_context():
        status, data = call("GET", f"{BASE_URL}/api/memory/{PROJECT_ID}/context")
        assert status == 200, status
        context = data.get("context", "")
        assert memory_text in context, context[:300]
        assert "No research context" not in context
        samples["memory_context_excerpt"] = context[-600:]
        return f"context length={len(context)}, contains new decision"

    def memory_forget():
        memory_id = memory_id_holder["id"]
        assert memory_id, "memory not saved"
        status, _ = call("DELETE", f"{BASE_URL}/api/memory/{PROJECT_ID}/{memory_id}")
        assert status == 200, status
        status, data = call("GET", f"{BASE_URL}/api/memory/{PROJECT_ID}")
        assert status == 200, status
        ids = [m.get("id") for m in data]
        assert memory_id not in ids, ids
        samples["memory_forget"] = {"deleted": memory_id, "remaining": len(ids)}
        return f"forgotten {memory_id}, remaining={len(ids)}"

    def report():
        status, data = call(
            "POST", f"{BASE_URL}/api/reports/weekly", {"project_id": PROJECT_ID}, timeout=120
        )
        assert status == 200, status
        report_text = data.get("report", "")
        assert len(report_text) > 2000, len(report_text)
        assert "Research Weekly Report" in report_text or "科研周报" in report_text
        assert "OOD" in report_text
        samples["report"] = {
            "length": len(report_text),
            "head": report_text[:800],
        }
        return f"{len(report_text)} chars, includes project experiments and memories"

    def persistence_files():
        data_dir = ROOT / "backend" / "data" / "powercontext"
        assert data_dir.exists(), data_dir
        files = sorted(p for p in data_dir.rglob("*") if p.is_file())
        assert files, "no files in PowerContext data dir"
        total = sum(p.stat().st_size for p in files)
        samples["powercontext_files"] = [
            {"path": str(p.relative_to(ROOT)), "size": p.stat().st_size} for p in files[:8]
        ]
        return f"{len(files)} files, {total / 1024 / 1024:.1f} MB under backend/data/powercontext"

    check("API health (seekdb + PowerContext)", health)
    check("PowerContext direct health + LabTrail scope", powercontext_direct)
    check("seekdb hybrid search", hybrid_search)
    check("seekdb vector search", vector_search)
    check("seekdb fulltext search", fulltext_search)
    check("Experiment data (30 records)", experiments)
    check("PowerContext save memory", memory_save)
    check("PowerContext search memory", memory_search)
    check("PowerContext recover context", memory_context)
    check("PowerContext forget memory", memory_forget)
    check("Weekly report generation", report)
    check("PowerContext persistence files", persistence_files)

    passed = sum(1 for c in checks if c["ok"])
    failed = len(checks) - passed
    summary = {"passed": passed, "failed": failed, "total": len(checks)}
    result = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "backend": BASE_URL,
        "powercontext": POWERCONTEXT_URL,
        "project_id": PROJECT_ID,
        "summary": summary,
        "checks": checks,
        "samples": samples,
    }
    (EVIDENCE / "verification.json").write_text(json.dumps(result, ensure_ascii=False, indent=2))

    lines = [
        "# LabTrail verification log",
        "",
        f"Generated: {result['generated_at']}",
        f"Backend: {BASE_URL}",
        f"PowerContext: {POWERCONTEXT_URL}",
        f"Project: {PROJECT_ID}",
        "",
        f"## Summary: {passed}/{len(checks)} passed, {failed} failed",
        "",
        "| # | Check | Result | Latency | Detail |",
        "| --- | --- | --- | --- | --- |",
    ]
    for i, c in enumerate(checks, 1):
        detail = str(c["detail"]).replace("|", "\\|").replace("\n", " ")
        lines.append(f"| {i} | {c['name']} | {'PASS' if c['ok'] else 'FAIL'} | {c['latency_ms']} ms | {detail} |")
    lines += ["", "## Samples", "```json", json.dumps(samples, ensure_ascii=False, indent=2), "```", ""]
    (EVIDENCE / "verification.log").write_text("\n".join(lines))

    print(f"\nResult: {passed}/{len(checks)} passed, {failed} failed")
    print(f"Wrote {EVIDENCE / 'verification.log'}")
    print(f"Wrote {EVIDENCE / 'verification.json'}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
