import numpy as np
from sentence_transformers import CrossEncoder
from app.config import RERANKER_MODEL_NAME

_reranker = None


def get_reranker() -> CrossEncoder:
    global _reranker
    if _reranker is None:
        _reranker = CrossEncoder(RERANKER_MODEL_NAME)
    return _reranker


def rerank(query: str, chunks: list[str]) -> list[tuple[str, float]]:
    reranker = get_reranker()
    pairs = [[query, chunk] for chunk in chunks]
    raw_scores = reranker.predict(pairs)

    # Sigmoid-normalize raw logits to a clean 0–1 relevance score
    scores = 1 / (1 + np.exp(-raw_scores))

    ranked = sorted(zip(chunks, scores.tolist()), key=lambda x: x[1], reverse=True)
    return ranked
