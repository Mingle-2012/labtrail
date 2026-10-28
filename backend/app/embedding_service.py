"""Embedding service using sentence-transformers (local, no API key needed)."""
import numpy as np
from sentence_transformers import SentenceTransformer
from app.config import EMBEDDING_MODEL

_model: SentenceTransformer | None = None

def get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer(EMBEDDING_MODEL)
    return _model

def get_embedding_dimension() -> int:
    return get_model().get_embedding_dimension()

def embed_texts(texts: list[str]) -> list[list[float]]:
    model = get_model()
    embeddings = model.encode(texts, show_progress_bar=False, normalize_embeddings=True)
    return embeddings.tolist()

def embed_query(text: str) -> list[float]:
    return embed_texts([text])[0]
