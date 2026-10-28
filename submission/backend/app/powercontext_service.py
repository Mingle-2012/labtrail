"""Research memory service using seekdb for persistent storage.

Note: PowerContext v1.4.1+ requires a server deployment. This implementation
uses seekdb for research memory storage, demonstrating the same concept of
persistent, project-isolated research context that survives across sessions.
"""
from __future__ import annotations

import json
import logging
import uuid
from typing import Any

from app.seekdb_service import get_or_create_collection

logger = logging.getLogger(__name__)

MEMORY_COLLECTION = "labtrail_research_memories"

_collection = None


def _get_collection() -> Any:
    global _collection
    if _collection is None:
        _collection = get_or_create_collection(MEMORY_COLLECTION)
    return _collection


def save_research_memory(
    project_id: str,
    content: str,
    memory_type: str = "conclusion",
    tags: list[str] | None = None,
) -> dict[str, Any]:
    collection = _get_collection()
    memory_id = f"mem_{uuid.uuid4().hex[:12]}"

    metadata = {
        "project_id": project_id,
        "memory_type": memory_type,
        "tags": ",".join(tags) if tags else "",
        "memory_id": memory_id,
    }

    collection.add(
        ids=[memory_id],
        documents=[content],
        metadatas=[metadata],
    )

    logger.info("Saved research memory for project %s: %s", project_id, content[:80])
    return {
        "id": memory_id,
        "content": content,
        "project_id": project_id,
        "memory_type": memory_type,
        "tags": tags or [],
    }


def search_research_memories(
    project_id: str,
    query: str,
    n_results: int = 10,
) -> list[dict[str, Any]]:
    collection = _get_collection()

    try:
        results = collection.query(
            query_texts=[query],
            n_results=n_results,
            where={"project_id": project_id},
            include=["documents", "metadatas", "distances"],
        )
    except Exception:
        results = collection.query(
            query_texts=[query],
            n_results=n_results,
            include=["documents", "metadatas", "distances"],
        )

    memories = []
    if results and results.get("documents"):
        docs = results["documents"][0] if results["documents"] else []
        metas = results.get("metadatas", [[]])[0] if results.get("metadatas") else []
        distances = results.get("distances", [[]])[0] if results.get("distances") else []

        for i, doc in enumerate(docs):
            meta = metas[i] if i < len(metas) else {}
            if meta.get("project_id") != project_id:
                continue
            memories.append({
                "content": doc,
                "metadata": meta,
                "score": float(distances[i]) if i < len(distances) else 0.0,
            })
    return memories


def get_project_memories(
    project_id: str,
    memory_type: str | None = None,
) -> list[dict[str, Any]]:
    collection = _get_collection()

    try:
        all_docs = collection.get(include=["documents", "metadatas"])
        if not all_docs or not all_docs.get("documents"):
            return []

        docs = all_docs["documents"]
        metas = all_docs.get("metadatas", [])
        ids = all_docs.get("ids", [])

        memories = []
        for i, doc in enumerate(docs):
            meta = metas[i] if i < len(metas) else {}
            if meta.get("project_id") != project_id:
                continue
            if memory_type and meta.get("memory_type") != memory_type:
                continue
            memories.append({
                "id": ids[i] if i < len(ids) else "",
                "content": doc,
                "metadata": meta,
            })
        return memories
    except Exception as e:
        logger.error("Error getting project memories: %s", e)
        return []


def delete_memory(project_id: str, memory_id: str) -> bool:
    collection = _get_collection()
    try:
        collection.delete(ids=[memory_id])
        return True
    except Exception as e:
        logger.error("Error deleting memory: %s", e)
        return False


def get_research_context(project_id: str) -> str:
    memories = get_project_memories(project_id)
    if not memories:
        return "No research context saved yet."
    context_parts = []
    for m in memories:
        mtype = m.get("metadata", {}).get("memory_type", "general")
        context_parts.append(f"[{mtype}] {m['content']}")
    return "\n".join(context_parts)
