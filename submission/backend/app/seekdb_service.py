"""seekdb service for document storage, vector search, and hybrid retrieval."""
from __future__ import annotations

import json
import logging
import uuid
from typing import Any

from pyseekdb import (
    Client,
    FulltextIndexConfig,
    Schema,
    VectorIndexConfig,
    IVFConfiguration,
)

from app.config import SEEKB_MODE, SEEKB_PATH, SEEKB_HOST, SEEKB_PORT
from app.embedding_service import get_embedding_dimension

logger = logging.getLogger(__name__)

_client = None
_collections: dict[str, Any] = {}

DOCS_COLLECTION = "labtrail_documents"
EXPERIMENTS_COLLECTION = "labtrail_experiments"


def get_client() -> Any:
    global _client
    if _client is None:
        if SEEKB_MODE == "embedded":
            _client = Client(path=SEEKB_PATH)
            logger.info("seekdb embedded client initialized at %s", SEEKB_PATH)
        else:
            _client = Client(host=SEEKB_HOST, port=SEEKB_PORT)
            logger.info("seekdb server client connected at %s:%s", SEEKB_HOST, SEEKB_PORT)
    return _client


def _get_schema() -> Schema:
    dim = get_embedding_dimension()
    return Schema(
        vector_index=VectorIndexConfig(
            ivf=IVFConfiguration(dimension=dim, distance="cosine"),
        ),
        fulltext_index=FulltextIndexConfig(),
    )


def get_or_create_collection(name: str) -> Any:
    if name in _collections:
        return _collections[name]
    client = get_client()
    collection = client.get_or_create_collection(
        name=name,
        schema=_get_schema(),
    )
    _collections[name] = collection
    logger.info("seekdb collection '%s' ready", name)
    return collection


def get_docs_collection() -> Any:
    return get_or_create_collection(DOCS_COLLECTION)


def get_experiments_collection() -> Any:
    return get_or_create_collection(EXPERIMENTS_COLLECTION)


def add_document_chunks(
    project_id: str,
    doc_id: str,
    chunks: list[dict[str, Any]],
) -> list[str]:
    if not chunks:
        return []
    collection = get_docs_collection()
    ids = []
    documents = []
    metadatas = []
    for chunk in chunks:
        chunk_id = f"{doc_id}_{uuid.uuid4().hex[:8]}"
        ids.append(chunk_id)
        documents.append(chunk["text"])
        metadatas.append({
            **chunk.get("metadata", {}),
            "doc_id": doc_id,
            "project_id": project_id,
        })
    collection.add(ids=ids, documents=documents, metadatas=metadatas)
    return ids


def search_documents(
    project_id: str,
    query: str,
    n_results: int = 10,
    where: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    collection = get_docs_collection()
    filter_where = {"project_id": project_id}
    if where:
        filter_where = {"$and": [filter_where, where]}

    try:
        results = collection.query(
            query_texts=[query],
            n_results=n_results,
            where=filter_where,
            include=["documents", "distances", "metadatas"],
        )
    except Exception:
        results = collection.query(
            query_texts=[query],
            n_results=n_results,
            include=["documents", "distances", "metadatas"],
        )

    search_results = []
    if results and results.get("documents"):
        docs = results["documents"][0] if results["documents"] else []
        distances = results.get("distances", [[]])[0] if results.get("distances") else []
        metas = results.get("metadatas", [[]])[0] if results.get("metadatas") else []
        rids = results.get("ids", [[]])[0] if results.get("ids") else []

        for i, doc in enumerate(docs):
            meta = metas[i] if i < len(metas) else {}
            if meta.get("project_id") and meta["project_id"] != project_id:
                continue
            search_results.append({
                "id": rids[i] if i < len(rids) else "",
                "text": doc,
                "score": float(distances[i]) if i < len(distances) else 0.0,
                "metadata": meta,
            })
    return search_results


def hybrid_search(
    project_id: str,
    query: str,
    n_results: int = 10,
    where: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    vector_results = search_documents(project_id, query, n_results=n_results * 2, where=where)

    ft_results_list = []
    try:
        collection = get_docs_collection()
        filter_where = {"project_id": project_id}
        ft_results = collection.query(
            query_texts=[query],
            n_results=n_results * 2,
            where=filter_where,
            include=["documents", "metadatas"],
            search_mode="fulltext",
        )
        ft_docs = ft_results.get("documents", [[]])[0] if ft_results.get("documents") else []
        ft_metas = ft_results.get("metadatas", [[]])[0] if ft_results.get("metadatas") else []
        ft_ids = ft_results.get("ids", [[]])[0] if ft_results.get("ids") else []

        for i, doc in enumerate(ft_docs):
            ft_results_list.append({
                "id": ft_ids[i] if i < len(ft_ids) else "",
                "text": doc,
                "metadata": ft_metas[i] if i < len(ft_metas) else {},
            })
    except Exception as e:
        logger.warning("Fulltext search fallback: %s", e)

    return _fuse_results(vector_results, ft_results_list, n_results)


def _fuse_results(
    vector_results: list[dict],
    ft_results: list[dict],
    n_results: int,
) -> list[dict]:
    k = 60
    scores: dict[str, float] = {}
    doc_map: dict[str, dict] = {}

    for rank, r in enumerate(vector_results):
        rid = r["id"]
        scores[rid] = scores.get(rid, 0.0) + 1.0 / (k + rank + 1)
        doc_map[rid] = r

    for rank, r in enumerate(ft_results):
        rid = r["id"]
        scores[rid] = scores.get(rid, 0.0) + 1.0 / (k + rank + 1)
        if rid not in doc_map:
            doc_map[rid] = r

    sorted_ids = sorted(scores.keys(), key=lambda x: scores[x], reverse=True)

    results = []
    for rid in sorted_ids[:n_results]:
        item = doc_map[rid].copy()
        item["score"] = scores[rid]
        item["fusion"] = True
        results.append(item)
    return results


def delete_document_chunks(project_id: str, doc_id: str) -> int:
    collection = get_docs_collection()
    try:
        all_docs = collection.get(include=["metadatas"])
        if not all_docs or not all_docs.get("ids"):
            return 0
        ids_to_delete = []
        metas = all_docs.get("metadatas", [])
        for i, meta in enumerate(metas):
            if meta and meta.get("doc_id") == doc_id and meta.get("project_id") == project_id:
                ids_to_delete.append(all_docs["ids"][i])
        if ids_to_delete:
            collection.delete(ids=ids_to_delete)
        return len(ids_to_delete)
    except Exception as e:
        logger.error("Error deleting document chunks: %s", e)
        return 0


def get_document_count(project_id: str) -> int:
    collection = get_docs_collection()
    try:
        all_docs = collection.get(include=["metadatas"])
        if not all_docs or not all_docs.get("metadatas"):
            return 0
        doc_ids = set()
        for meta in all_docs.get("metadatas", []):
            if meta and meta.get("doc_id") and meta.get("project_id") == project_id:
                doc_ids.add(meta["doc_id"])
        return len(doc_ids)
    except Exception:
        return 0


def get_chunk_count(project_id: str) -> int:
    collection = get_docs_collection()
    try:
        all_docs = collection.get(include=["metadatas"])
        if not all_docs or not all_docs.get("metadatas"):
            return 0
        count = 0
        for meta in all_docs.get("metadatas", []):
            if meta and meta.get("project_id") == project_id:
                count += 1
        return count
    except Exception:
        return 0
