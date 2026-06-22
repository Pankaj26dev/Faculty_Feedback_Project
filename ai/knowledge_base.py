import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple

try:
    import pandas as pd
except Exception:
    pd = None

__all__ = ["load_taxonomy", "get_theme_keyword_map", "find_taxonomy_file"]


def find_taxonomy_file(root: Optional[str] = None) -> Optional[str]:
    """Return the path to the taxonomy file (Excel or CSV) if found, else None."""
    if root is None:
        root = Path(__file__).resolve().parents[1]

    root = Path(root)

    # Candidate filenames (prefer Excel)
    candidates = [
        "faculty_feedback_taxonomy_v2.xlsx",
        "faculty_feedback_taxonomy_v2.xls",
        "faculty_feedback_taxonomy_v2.csv",
    ]

    for name in candidates:
        p = root / name
        if p.exists():
            return str(p)

    # fallback: search any matching file in root
    for p in root.iterdir():
        if p.name.lower().startswith("faculty_feedback_taxonomy_v2") and p.suffix.lower() in [".csv", ".xlsx", ".xls"]:
            return str(p)

    return None


def _split_keywords(cell_value: Optional[str]) -> List[str]:
    if cell_value is None:
        return []
    if not isinstance(cell_value, str):
        cell_value = str(cell_value)
    parts = [p.strip() for p in cell_value.split("|") if p.strip()]
    return parts


def load_taxonomy(path: Optional[str] = None):
    """Load the taxonomy file and return a pandas.DataFrame-like object.

    - If `pandas` is available it returns a `pd.DataFrame`.
    - If `pandas` is not available it returns a list of dicts parsed from CSV.

    The function will try Excel first, then CSV. Pass an explicit `path` to override detection.
    """
    if path is None:
        path = find_taxonomy_file()

    if path is None:
        raise FileNotFoundError("Taxonomy file not found in project root")

    path = Path(path)

    if pd is not None:
        try:
            if path.suffix.lower() in [".xls", ".xlsx"]:
                df = pd.read_excel(path)
            else:
                df = pd.read_csv(path)
        except Exception:
            # fallback to CSV read
            df = pd.read_csv(path)

        # normalize columns
        expected_columns = [
            "theme_id",
            "category",
            "theme_name",
            "sentiment",
            "recommendation",
            "keyword_patterns",
            "broken_english_patterns",
            "normal_english_patterns",
            "advanced_English_patterns",
        ]

        # ensure present
        for col in expected_columns:
            if col not in df.columns:
                df[col] = ""

        return df

    # Minimal CSV fallback without pandas
    import csv

    rows = []
    with open(path, newline='', encoding='utf-8') as fh:
        reader = csv.DictReader(fh)
        for r in reader:
            rows.append(r)

    return rows


def get_theme_keyword_map(path: Optional[str] = None) -> Dict[str, Dict[str, List[str]]]:
    """Return a mapping of theme_id -> { 'theme_name': str, 'keywords': [...], 'patterns': {...} }.

    The `keywords` list is derived from the `keyword_patterns` column (split by '|').
    Additional pattern columns are returned under `patterns`.
    """
    data = load_taxonomy(path)

    out: Dict[str, Dict[str, List[str]]] = {}

    if hasattr(data, "iterrows"):
        # pandas DataFrame
        for _, row in data.iterrows():
            tid = str(row.get("theme_id", "")).strip()
            tname = str(row.get("theme_name", "")).strip()
            keywords = _split_keywords(row.get("keyword_patterns", ""))
            patterns = {
                "broken_english": _split_keywords(row.get("broken_english_patterns", "")),
                "normal_english": _split_keywords(row.get("normal_english_patterns", "")),
                "advanced_English": _split_keywords(row.get("advanced_English_patterns", "")),
            }
            out[tid] = {"theme_name": tname, "keywords": keywords, "patterns": patterns}
    else:
        # list of dicts
        for row in data:
            tid = str(row.get("theme_id", "")).strip()
            tname = str(row.get("theme_name", "")).strip()
            keywords = _split_keywords(row.get("keyword_patterns", ""))
            patterns = {
                "broken_english": _split_keywords(row.get("broken_english_patterns", "")),
                "normal_english": _split_keywords(row.get("normal_english_patterns", "")),
                "advanced_English": _split_keywords(row.get("advanced_English_patterns", "")),
            }
            out[tid] = {"theme_name": tname, "keywords": keywords, "patterns": patterns}

    return out
