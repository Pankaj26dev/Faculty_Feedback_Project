from typing import List, Tuple, Dict, Optional

from ai.knowledge_base import get_theme_keyword_map
from ai.semantic_analysis import load_model, build_theme_embeddings, detect_themes

_cached_theme_map: Optional[Dict[str, Dict]] = None
_cached_model = None
_cached_theme_ids: Optional[List[str]] = None
_cached_theme_embs = None
_cached_model_name: Optional[str] = None


def get_recommendations_for_theme_ids(theme_ids: List[Tuple[str, float]], theme_map: Dict[str, Dict]) -> List[Tuple[str, str, float]]:
    """Map list of (theme_id, score) to (theme_id, recommendation, score).

    If a theme has no recommendation text, falls back to the theme name.
    """
    out = []
    for tid, score in theme_ids:
        info = theme_map.get(tid, {})
        rec = info.get("recommendation") if info else None
        if rec is None or rec == "":
            rec = info.get("theme_name", tid)
        out.append((tid, rec, score))
    return out


def _prepare_cached_resources(model_name: str = "all-MiniLM-L6-v2"):
    global _cached_theme_map, _cached_model, _cached_theme_ids, _cached_theme_embs, _cached_model_name

    if _cached_theme_map is None:
        _cached_theme_map = get_theme_keyword_map()

    if _cached_model is None or _cached_model_name != model_name:
        _cached_model = load_model(model_name)
        _cached_model_name = model_name
        _cached_theme_ids, _cached_theme_embs = build_theme_embeddings(_cached_theme_map, _cached_model)

    if _cached_theme_ids is None or _cached_theme_embs is None:
        _cached_theme_ids, _cached_theme_embs = build_theme_embeddings(_cached_theme_map, _cached_model)

    return _cached_theme_map, _cached_model, _cached_theme_ids, _cached_theme_embs


def recommend_from_text(text: str, top_k: int = 3, min_score: float = 0.35, model_name: str = "all-MiniLM-L6-v2") -> List[Tuple[str, str, float]]:
    """Given a feedback text, detect themes and return recommendations as (theme_id, recommendation, score)."""
    theme_map, model, theme_ids, theme_embs = _prepare_cached_resources(model_name)
    detected = detect_themes(text, theme_ids, theme_embs, model, top_k=top_k, min_score=min_score)
    recs = get_recommendations_for_theme_ids(detected, theme_map)
    return recs


if __name__ == "__main__":
    # quick manual test
    sample = "The lecture is too fast and slides are read word for word."
    recs = recommend_from_text(sample)
    print("Recommendations for:\n", sample)
    for tid, rec, score in recs:
        print(tid, round(score, 3), "->", rec)
