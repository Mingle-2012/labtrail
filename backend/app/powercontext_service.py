"""Research memory service backed by a local PowerContext Server.

Memories are written to and searched through PowerContext's Memory API.
LabTrail projects map 1:1 to PowerContext scopes, which provides project
isolation; kind maps to the LabTrail memory type.
"""
from __future__ import annotations

import logging
import os
import threading
from typing import Any

import httpx

logger = logging.getLogger(__name__)

POWERCONTEXT_URL = os.getenv("POWERCONTEXT_URL", "http://127.0.0.1:8890").rstrip("/")
POWERCONTEXT_TIMEOUT = float(os.getenv("POWERCONTEXT_TIMEOUT", "15"))

_scopes: dict[str, str] = {}
_scope_lock = threading.Lock()


def _request(method: str, path: str, **kwargs: Any) -> dict[str, Any]:
    with httpx.Client(base_url=POWERCONTEXT_URL, timeout=POWERCONTEXT_TIMEOUT) as client:
        response = client.request(method, path, **kwargs)
        response.raise_for_status()
        return response.json()


def powercontext_health() -> dict[str, Any]:
    try:
        with httpx.Client(base_url=POWERCONTEXT_URL, timeout=3) as client:
            response = client.get("/health/ready")
        ready = response.status_code == 200 and response.json().get("status") == "ready"
        return {"url": POWERCONTEXT_URL, "status": "ready" if ready else "unavailable"}
    except Exception as error:  # noqa: BLE001 - health output is best effort
        return {"url": POWERCONTEXT_URL, "status": "unavailable", "error": str(error)}


def _scope_title(project_id: str) -> str:
    return f"LabTrail · {project_id}"


def _ensure_scope(project_id: str) -> str:
    with _scope_lock:
        cached = _scopes.get(project_id)
        if cached:
            return cached

        scopes = _request("GET", "/v1/scopes").get("items", [])
        for scope in scopes:
            if scope.get("title") == _scope_title(project_id):
                _scopes[project_id] = scope["scope_id"]
                return scope["scope_id"]

        created = _request(
            "POST",
            "/v1/scopes",
            json={
                "title": _scope_title(project_id),
                "summary": f"Research memory for LabTrail project {project_id}",
                "idempotency_key": f"labtrail-scope-{project_id}",
            },
        )
        _scopes[project_id] = created["scope_id"]
        logger.info("Created PowerContext scope %s for project %s", created["scope_id"], project_id)
        return created["scope_id"]


def _scope_request(project_id: str, method: str, path: str, payload: dict[str, Any]) -> dict[str, Any]:
    """Call a scope-bound endpoint, refreshing a stale scope cache once."""
    scope_id = _ensure_scope(project_id)
    try:
        return _request(method, path, json={**payload, "scope_id": scope_id})
    except httpx.HTTPStatusError as error:
        if error.response.status_code not in (404, 409, 500):
            raise
        logger.warning("PowerContext scope %s for %s seems stale; refreshing", scope_id, project_id)
        with _scope_lock:
            _scopes.pop(project_id, None)
        scope_id = _ensure_scope(project_id)
        return _request(method, path, json={**payload, "scope_id": scope_id})


def _memory_metadata(project_id: str, memory_type: str, memory_id: str, tags: list[str] | None = None) -> dict[str, Any]:
    return {
        "project_id": project_id,
        "memory_type": memory_type,
        "tags": ",".join(tags or []),
        "memory_id": memory_id,
    }


def save_research_memory(
    project_id: str,
    content: str,
    memory_type: str = "conclusion",
    tags: list[str] | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "kind": memory_type or "general",
        "text": content,
    }
    if tags:
        payload["reason"] = f"tags: {','.join(tags)}"

    result = _scope_request(project_id, "POST", "/v1/memory/remember", payload)
    scope_id = _scopes.get(project_id, "")
    record = (result.get("records") or [{}])[0]
    artifact_id = record.get("artifact", {}).get("artifact_id", "")

    logger.info("Saved research memory for project %s: %s", project_id, content[:80])
    return {
        "id": artifact_id,
        "content": content,
        "project_id": project_id,
        "memory_type": memory_type,
        "tags": tags or [],
        "scope_id": scope_id,
        "changed": result.get("changed", True),
    }


def search_research_memories(
    project_id: str,
    query: str,
    n_results: int = 10,
) -> list[dict[str, Any]]:
    result = _scope_request(
        project_id,
        "POST",
        "/v1/memory/search",
        {"query": query, "limit": n_results, "mode": "auto"},
    )

    memories = []
    for hit in result.get("hits", []):
        memory = hit.get("memory", {})
        artifact_id = memory.get("artifact", {}).get("artifact_id", "")
        memories.append({
            "id": artifact_id,
            "content": memory.get("text", ""),
            "metadata": _memory_metadata(project_id, memory.get("kind", "general"), artifact_id),
            "score": float(hit.get("score", 0.0)),
            "matched_by": hit.get("matched_by", []),
            "mode": result.get("mode"),
        })
    return memories


def get_project_memories(
    project_id: str,
    memory_type: str | None = None,
) -> list[dict[str, Any]]:
    result = _scope_request(project_id, "POST", "/v1/memory/entries/list", {"limit": 100})

    memories = []
    for entry in result.get("entries", []):
        if entry.get("state") != "active":
            continue
        if memory_type and entry.get("kind") != memory_type:
            continue
        artifact = entry.get("artifact", {})
        artifact_id = artifact.get("artifact_id", "")
        memories.append({
            "id": artifact_id,
            "content": entry.get("text", ""),
            "metadata": _memory_metadata(project_id, entry.get("kind", "general"), artifact_id),
            "state": entry.get("state"),
            "state_version": entry.get("state_version", 0),
            "artifact": artifact,
        })
    return memories


def delete_memory(project_id: str, memory_id: str) -> bool:
    target = next((m for m in get_project_memories(project_id) if m["id"] == memory_id), None)
    if target is None:
        return False

    _scope_request(
        project_id,
        "POST",
        "/v1/atomic-memory/lifecycle",
        {
            "target": {
                "artifact": target["artifact"],
                "state_version": target["state_version"],
            },
            "state": "forgotten",
        },
    )
    return True


def get_research_context(project_id: str) -> str:
    memories = get_project_memories(project_id)
    if not memories:
        return "No research context saved yet."
    context_parts = []
    for memory in memories:
        memory_type = memory.get("metadata", {}).get("memory_type", "general")
        context_parts.append(f"[{memory_type}] {memory['content']}")
    return "\n".join(context_parts)
