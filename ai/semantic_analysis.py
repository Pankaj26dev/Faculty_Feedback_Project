from typing import Dict, List, Tuple, Optional
from pathlib import Path
import os

import numpy as np

try:
    from sentence_transformers import SentenceTransformer
except Exception:
    SentenceTransformer = None

from ai.knowledge_base import get_theme_keyword_map, find_taxonomy_file

EMBED_CACHE = Path(__file__).resolve().parent / "theme_embeddings.npz"


def load_model(model_name: str = "all-MiniLM-L6-v2") -> SentenceTransformer:
    if SentenceTransformer is None:
        raise ImportError("sentence-transformers is not installed. Install via requirements.txt")
    return SentenceTransformer(model_name)


def _aggregate_texts_for_theme(theme_info: Dict) -> str:
    parts = [theme_info.get("theme_name", "")] + theme_info.get("keywords", [])
    # also include patterns
    for k, v in theme_info.get("patterns", {}).items():
        parts.extend(v)
    # join into a single representative string
    return " . ".join(parts)


def build_theme_embeddings(theme_map: Dict[str, Dict], model: SentenceTransformer, force_rebuild: bool = False) -> Tuple[List[str], np.ndarray]:
    """Return (theme_ids, embeddings_array).

    Embeddings are cached to `ai/theme_embeddings.npz` to speed up repeated runs.
    """
    theme_ids = list(theme_map.keys())

    if EMBED_CACHE.exists() and not force_rebuild:
        try:
            data = np.load(EMBED_CACHE, allow_pickle=True)
            cached_ids = data["ids"].tolist()
            if cached_ids == theme_ids:
                return theme_ids, data["embeddings"]
        except Exception:
            pass

    texts = [_aggregate_texts_for_theme(theme_map[tid]) for tid in theme_ids]
    embeddings = model.encode(texts, convert_to_numpy=True, show_progress_bar=False)

    # save cache
    try:
        np.savez_compressed(EMBED_CACHE, ids=np.array(theme_ids, dtype=object), embeddings=embeddings)
    except Exception:
        pass

    return theme_ids, embeddings


def detect_themes(text: str, theme_ids: List[str], theme_embeddings: np.ndarray, model: SentenceTransformer, top_k: int = 3, min_score: float = 0.45) -> List[Tuple[str, float]]:
    """Return a list of (theme_id, score) sorted by score descending.

    Scores below `min_score` are filtered out.
    """
    if not text:
        return []

    query_emb = model.encode([text], convert_to_numpy=True, show_progress_bar=False)[0]

    # cosine similarity
    # normalize
    def _norm(x):
        denom = np.linalg.norm(x)
        return x / denom if denom > 0 else x

    qn = _norm(query_emb)
    emn = np.array([_norm(e) for e in theme_embeddings])

    sims = (emn @ qn).tolist()

    scored = list(zip(theme_ids, sims))
    scored.sort(key=lambda x: x[1], reverse=True)

    # filter by min_score
    result = [(tid, float(score)) for tid, score in scored if score >= min_score]
    return result[:top_k]


if __name__ == "__main__":
    # quick CLI test
    tm = get_theme_keyword_map()
    model = load_model()
    ids, embs = build_theme_embeddings(tm, model)
    samples = [
        "Lecture pace is too fast and hard to follow.",
        "Great explanations, very clear and helpful.",
    ]
    for s in samples:
        print("\nInput:", s)
        matches = detect_themes(s, ids, embs, model, top_k=3)
        for tid, score in matches:
            print(tid, tm[tid]["theme_name"], round(score, 3))
