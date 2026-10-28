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

from app.config import SEEKDB_MODE, SEEKDB_PATH, SEEKDB_HOST, SEEKDB_PORT
from app.embedding_service import get_embedding_dimension

logger = logging.getLogger(__name__)

_client = None
_collections: dict[str, Any] = {}

DOCS_COLLECTION = "labtrail_documents"


def get_client() -> Any:
    global _client
    if _client is None:
        if SEEKDB_MODE == "embedded":
            _client = Client(path=SEEKDB_PATH)
            logger.info("seekdb embedded client initialized at %s", SEEKDB_PATH)
        else:
            _client = Client(host=SEEKDB_HOST, port=SEEKDB_PORT)
            logger.info("seekdb server client connected at %s:%s", SEEKDB_HOST, SEEKDB_PORT)
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


def _project_where(project_id: str, where: dict[str, Any] | None = None) -> dict[str, Any]:
    if where:
        return {"$and": [{"project_id": project_id}, where]}
    return {"project_id": project_id}


def _rows_to_results(result: dict[str, Any], score_from_distance: bool) -> list[dict[str, Any]]:
    docs = result.get("documents", [[]])[0] if result.get("documents") else []
    metas = result.get("metadatas", [[]])[0] if result.get("metadatas") else []
    ids = result.get("ids", [[]])[0] if result.get("ids") else []
    scores = result.get("distances", [[]])[0] if result.get("distances") else []

    results = []
    for i, doc in enumerate(docs):
        raw = float(scores[i]) if i < len(scores) else 0.0
        results.append({
            "id": ids[i] if i < len(ids) else "",
            "text": doc,
            "score": 1.0 - raw if score_from_distance else raw,
            "metadata": metas[i] if i < len(metas) else {},
        })
    return results


def search_documents(
    project_id: str,
    query: str,
    n_results: int = 10,
    where: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """Dense vector search. Scores are cosine similarity (1 - cosine distance)."""
    collection = get_docs_collection()
    results = collection.query(
        query_texts=[query],
        n_results=n_results,
        where=_project_where(project_id, where),
        include=["documents", "distances", "metadatas"],
    )
    return _rows_to_results(results, score_from_distance=True)


def fulltext_search(
    project_id: str,
    query: str,
    n_results: int = 10,
    where: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """Full-text search on the seekdb FULLTEXT index. Scores are relevance, higher is better."""
    collection = get_docs_collection()
    results = collection.hybrid_search(
        query={
            "where_document": {"$contains": query},
            "where": _project_where(project_id, where),
            "n_results": n_results,
        },
        n_results=n_results,
        include=["documents", "metadatas", "distances"],
    )
    return _rows_to_results(results, score_from_distance=False)


def hybrid_search(
    project_id: str,
    query: str,
    n_results: int = 10,
    where: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """Native seekdb hybrid search: vector KNN + FULLTEXT, fused by RRF."""
    collection = get_docs_collection()
    filter_where = _project_where(project_id, where)
    results = collection.hybrid_search(
        query={
            "where_document": {"$contains": query},
            "where": filter_where,
            "n_results": n_results,
        },
        knn={
            "query_texts": [query],
            "where": filter_where,
            "n_results": n_results,
        },
        rank={"rrf": {"rank_window_size": 60, "rank_constant": 60}},
        n_results=n_results,
        include=["documents", "metadatas", "distances"],
    )
    return _rows_to_results(results, score_from_distance=False)


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
