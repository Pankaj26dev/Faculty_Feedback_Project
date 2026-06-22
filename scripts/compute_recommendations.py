#!/usr/bin/env python3
"""Batch script to compute theme recommendations for feedback rows.

Usage:
  python scripts/compute_recommendations.py

This script finds feedback rows where `theme_ids` is empty and fills
`theme_ids`, `recommendations`, and `theme_scores` using the local taxonomy
and sentence-transformers model. It loads the model and embeddings once.
"""
import sqlite3
import json
from pathlib import Path
from typing import List, Tuple

from ai.knowledge_base import get_theme_keyword_map
from ai.semantic_analysis import load_model, build_theme_embeddings, detect_themes
from ai.recommendation_engine import get_recommendations_for_theme_ids


DB = Path(__file__).resolve().parents[1] / "database" / "feedback.db"


def rows_missing_themes(conn: sqlite3.Connection) -> List[Tuple[int, str]]:
    cur = conn.cursor()
    cur.execute("SELECT id, feedback_text FROM feedback WHERE theme_ids IS NULL OR trim(theme_ids) = ''")
    return cur.fetchall()


def update_row(conn: sqlite3.Connection, row_id: int, theme_ids: List[str], recs: List[str], scores: List[float]):
    cur = conn.cursor()
    cur.execute(
        "UPDATE feedback SET theme_ids = ?, recommendations = ?, theme_scores = ? WHERE id = ?",
        (json.dumps(theme_ids, ensure_ascii=False), json.dumps(recs, ensure_ascii=False), json.dumps(scores, ensure_ascii=False), row_id),
    )
    conn.commit()


def main():
    print("DB:", DB)
    conn = sqlite3.connect(str(DB))

    pending = rows_missing_themes(conn)
    print(f"Rows missing themes: {len(pending)}")

    if not pending:
        conn.close()
        return

    print("Loading taxonomy and model (this may take a minute)...")
    theme_map = get_theme_keyword_map()
    model = load_model()
    theme_ids, theme_embs = build_theme_embeddings(theme_map, model)

    for idx, (row_id, feedback_text) in enumerate(pending, start=1):
        try:
            matches = detect_themes(feedback_text, theme_ids, theme_embs, model, top_k=5, min_score=0.35)
            recs = get_recommendations_for_theme_ids(matches, theme_map)

            ids = [t for t, s in matches]
            rec_texts = [r for t, r, s in recs]
            scores = [s for t, s in matches]

            update_row(conn, row_id, ids, rec_texts, scores)
            print(f"[{idx}/{len(pending)}] Updated id={row_id} -> {ids}")
        except Exception as e:
            print(f"[{idx}/{len(pending)}] Failed id={row_id}: {e}")

    conn.close()


if __name__ == "__main__":
    main()
