"""Embedding helper backed by pyseekdb's bundled all-MiniLM-L6-v2 ONNX model.

The same embedding function embeds documents and queries, so index-time and
query-time vectors stay consistent. No API key or external service is needed.
"""
from __future__ import annotations

from pyseekdb import DefaultEmbeddingFunction

_embedding_function: DefaultEmbeddingFunction | None = None


def get_embedding_function() -> DefaultEmbeddingFunction:
    global _embedding_function
    if _embedding_function is None:
        _embedding_function = DefaultEmbeddingFunction()
    return _embedding_function


def get_embedding_dimension() -> int:
    return get_embedding_function().dimension


def embed_texts(texts: list[str]) -> list[list[float]]:
    return get_embedding_function()(texts)
