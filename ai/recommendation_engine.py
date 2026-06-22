from typing import List, Tuple, Dict, Optional

from ai.knowledge_base import get_theme_keyword_map
from ai.semantic_analysis import load_model, build_theme_embeddings, detect_themes


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


def recommend_from_text(text: str, top_k: int = 3, min_score: float = 0.35, model_name: str = "all-MiniLM-L6-v2") -> List[Tuple[str, str, float]]:
    """Given a feedback text, detect themes and return recommendations as (theme_id, recommendation, score).

    This loads the taxonomy and sentence-transformers model (unless already cached by the library).
    """
    theme_map = get_theme_keyword_map()

    model = load_model(model_name)
    theme_ids, theme_embs = build_theme_embeddings(theme_map, model)

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
