"""Export a real data snapshot from a running LabTrail backend for the static website."""
from __future__ import annotations

import json
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

BASE_URL = "http://127.0.0.1:8000"
PROJECT_ID = "demo_project"
OUT_PATH = Path(__file__).resolve().parent.parent / "web" / "assets" / "data" / "demo.json"

QUERIES = [
    {
        "id": "ood",
        "label": "OOD 查询为何退化",
        "text": "Why does OOD query distribution degrade graph index performance?",
    },
    {
        "id": "vamana",
        "label": "Vamana 剪枝参数",
        "text": "How does the Vamana alpha pruning parameter affect recall?",
    },
    {
        "id": "tradeoff",
        "label": "召回率与吞吐权衡",
        "text": "What is the recall and QPS tradeoff for graph indexes?",
    },
    {
        "id": "construction",
        "label": "分布感知建图",
        "text": "How to build a query distribution-aware graph index?",
    },
]

MODES = ["hybrid", "vector", "fulltext"]


def request(method: str, path: str, payload: dict | None = None):
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(
        BASE_URL + path,
        data=data,
        method=method,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=120) as response:
        return json.loads(response.read())


def pivot_experiments(records: list[dict]) -> list[dict]:
    grouped: dict[tuple, dict] = {}
    for record in records:
        key = (record["method"], record["dataset"], record["timestamp"])
        row = grouped.setdefault(
            key,
            {
                "method": record["method"],
                "dataset": record["dataset"],
                "timestamp": record["timestamp"],
                "parameters": record.get("parameters", {}),
            },
        )
        row[record["metric_name"]] = record["metric_value"]
    return list(grouped.values())


def trim_search(payload: dict) -> dict:
    return {
        "mode": payload["mode"],
        "count": payload["count"],
        "results": [
            {
                "text": item["text"],
                "score": item["score"],
                "file_name": item["metadata"].get("file_name", ""),
                "source": item["metadata"].get("source", ""),
                "page": item["metadata"].get("page"),
                "doc_id": item["metadata"].get("doc_id", ""),
            }
            for item in payload["results"][:5]
        ],
    }


def main() -> None:
    project = request("GET", f"/api/projects/{PROJECT_ID}")
    dashboard = request("GET", f"/api/projects/{PROJECT_ID}/dashboard")
    memories = request("GET", f"/api/memory/{PROJECT_ID}")
    context = request("GET", f"/api/memory/{PROJECT_ID}/context")
    experiments = request("GET", f"/api/experiments/{PROJECT_ID}")
    recall_qps = request("GET", f"/api/experiments/{PROJECT_ID}/recall-qps")
    report = request("POST", "/api/reports/weekly", {"project_id": PROJECT_ID})["report"]

    search = {}
    for query in QUERIES:
        search[query["id"]] = {}
        for mode in MODES:
            payload = request(
                "POST",
                f"/api/documents/search?project_id={PROJECT_ID}",
                {"query": query["text"], "mode": mode, "n_results": 5},
            )
            search[query["id"]][mode] = trim_search(payload)

    snapshot = {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "source": "LabTrail backend running locally with seekdb 1.4.0 + PowerContext 1.4.1",
        "project": {
            "id": project["id"],
            "name": project["name"],
            "description": project["description"],
            "research_direction": project.get("research_direction", ""),
            "goal": project.get("goal", ""),
        },
        "dashboard": {
            "total_documents": dashboard["total_documents"],
            "total_chunks": dashboard["total_chunks"],
            "total_experiments": dashboard["total_experiments"],
            "total_memories": dashboard["total_memories"],
            "methods": dashboard["methods"],
            "datasets": dashboard["datasets"],
        },
        "queries": QUERIES,
        "search": search,
        "memories": [
            {
                "id": memory["id"],
                "content": memory["content"],
                "type": memory["metadata"].get("memory_type", "general"),
                "state": memory.get("state", "active"),
            }
            for memory in memories
        ],
        "memory_context": context["context"],
        "experiments": pivot_experiments(experiments["records"]),
        "recall_qps": recall_qps,
        "experiment_summary": {
            "methods": experiments["methods"],
            "datasets": experiments["datasets"],
            "summary": experiments["summary"],
        },
        "report": report,
    }

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {OUT_PATH} ({OUT_PATH.stat().st_size} bytes)")
    print(
        f"documents={snapshot['dashboard']['total_documents']} "
        f"experiments={snapshot['dashboard']['total_experiments']} "
        f"memories={snapshot['dashboard']['total_memories']}"
    )


if __name__ == "__main__":
    main()
