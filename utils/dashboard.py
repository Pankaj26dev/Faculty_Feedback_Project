import json
from collections import Counter
from typing import Dict, List, Tuple

import pandas as pd
import streamlit as st

from ai.knowledge_base import get_theme_keyword_map
from ai.recommendation_engine import recommend_from_text
from database.db import fetch_feedback, get_all_faculty_subject_map


def _safe_json_load(value):
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, str):
        value = value.strip()
        if value == "":
            return []
        try:
            return json.loads(value)
        except Exception:
            return [value]
    return []


def _theme_counts_from_feedback(feedback_texts: List[str], stored_theme_ids: List[str], theme_map: Dict[str, Dict]) -> List[Tuple[str, int]]:
    counts = Counter(stored_theme_ids)
    if not counts:
        return []
    return [(theme_map.get(tid, {}).get("theme_name", tid), counts[tid]) for tid, _ in counts.most_common()]


def _parse_feedback_rows(rows):
    if not rows:
        return pd.DataFrame()

    first = rows[0]
    if len(first) >= 10:
        columns = [
            "ID",
            "Student",
            "Faculty",
            "Subject",
            "Rating",
            "Feedback",
            "Sentiment",
            "Theme IDs",
            "Recommendations",
            "Theme Scores",
        ]
        if len(first) > len(columns):
            columns += [f"Extra_{i}" for i in range(len(columns), len(first))]
    else:
        columns = [f"col_{i}" for i in range(len(first))]
    df = pd.DataFrame(rows, columns=columns)
    return df


def _aggregate_recommendations(df: pd.DataFrame, theme_map: Dict[str, Dict], fallback: bool = True) -> List[str]:
    recs = []
    generic_terms = {"Average / Neutral Feedback", "Mixed: Good Knowledge, Poor Delivery", "No Specific Feedback", "General"}
    
    if "Recommendations" in df.columns:
        for raw in df["Recommendations"]:
            for value in _safe_json_load(raw):
                if isinstance(value, str) and value.strip():
                    val = value.strip()
                    if val not in generic_terms:
                        recs.append(val)
    
    # Deduplicate and filter
    filtered_recs = []
    seen = set()
    for rec in recs:
        if rec not in seen and rec not in generic_terms:
            filtered_recs.append(rec)
            seen.add(rec)
    
    if filtered_recs:
        return filtered_recs

    if fallback:
        texts = df["Feedback"].astype(str).tolist()[:8]
        out = []
        for text in texts:
            if not text.strip():
                continue
            try:
                theme_recs = recommend_from_text(text, top_k=2)
                for _, rec, score in theme_recs:
                    if rec and rec not in out and rec not in generic_terms:
                        out.append(rec)
            except Exception:
                continue
        return out
    return []


def _top_themes(df: pd.DataFrame, theme_map: Dict[str, Dict], positive: bool = True, top_n: int = 4) -> List[str]:
    generic_terms = {"Average / Neutral Feedback", "Mixed: Good Knowledge, Poor Delivery", "No Specific Feedback", "General"}
    
    if "Theme IDs" in df.columns:
        theme_ids = []
        for raw in df["Theme IDs"]:
            theme_ids.extend(_safe_json_load(raw))
        if theme_ids:
            counts = Counter(theme_ids)
            names = [
                theme_map.get(tid, {}).get("theme_name", tid) 
                for tid, _ in counts.most_common(top_n * 2)  # Get more, then filter
            ]
            # Filter out generic items
            names = [n for n in names if n not in generic_terms][:top_n]
            return names

    # Fallback: use stored recommendations by theme names or raw text
    sentiments = df["Sentiment"].astype(str).str.lower() if "Sentiment" in df.columns else None
    if sentiments is not None:
        subset = df[sentiments.str.contains("positive") if positive else ~sentiments.str.contains("positive")]
    else:
        subset = df
    texts = subset["Feedback"].astype(str).tolist()[:8]
    candidates = []
    for text in texts:
        try:
            theme_recs = recommend_from_text(text, top_k=2)
            candidates.extend([rec for _, rec, _ in theme_recs if rec not in generic_terms])
        except Exception:
            continue
    counts = Counter(candidates)
    result = [name for name, _ in counts.most_common(top_n) if name not in generic_terms]
    return result


def render_faculty_dashboard():
    st.title("Unfiltered: Faculty Insight & Feedback Analytics")
    faculty_map = get_all_faculty_subject_map()
    faculty_names = list(faculty_map.keys())

    if not faculty_names:
        st.warning("No faculty records are available yet. Add at least one faculty with feedback first.")
        return

    selected = st.selectbox("Select faculty to review", ["Choose faculty..."] + faculty_names)
    if selected == "Choose faculty...":
        st.info("Select a faculty member to load dashboard insights.")
        return

    subject = faculty_map.get(selected, "Unknown subject")
    rows = fetch_feedback()
    df = _parse_feedback_rows(rows)
    df = df[df["Faculty"] == selected] if "Faculty" in df.columns else df
    if df.empty:
        st.warning(f"No feedback yet for {selected}.")
        return

    # Header row
    st.markdown("---")
    cols = st.columns([2, 2, 2, 2])
    cols[0].markdown(f"**Faculty:** {selected}")
    cols[1].markdown(f"**Subject:** {subject}")
    cols[2].markdown(f"**Total Feedback:** {len(df)}")
    cols[3].markdown(f"**Average Rating:** {round(df['Rating'].mean(), 2)}")
    st.markdown("---")

    # KPI cards
    sentiment_counts = df["Sentiment"].value_counts().to_dict()
    positive = sentiment_counts.get("Positive", 0)
    neutral = sentiment_counts.get("Neutral", 0)
    negative = sentiment_counts.get("Negative", 0)

    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("Total", len(df))
    k2.metric("Avg Rating", round(df["Rating"].mean(), 2))
    k3.metric("Positive", positive)
    k4.metric("Neutral", neutral)
    k5.metric("Negative", negative)

    st.markdown("---")

    # Charts
    chart_cols = st.columns(2)
    try:
        import plotly.express as px

        rating_series = df["Rating"].value_counts().sort_index().reset_index()
        rating_series.columns = ["Rating", "Count"]
        fig_dist = px.bar(rating_series, x="Rating", y="Count", title="Rating Distribution", labels={"Rating": "Rating", "Count": "Count"})
        chart_cols[0].plotly_chart(fig_dist, use_container_width=True)

        sentiment_series = pd.DataFrame(
            [(k, v) for k, v in sentiment_counts.items()], columns=["Sentiment", "Count"]
        )
        fig_sent = px.pie(sentiment_series, names="Sentiment", values="Count", title="Sentiment Distribution")
        chart_cols[1].plotly_chart(fig_sent, use_container_width=True)
    except Exception:
        chart_cols[0].warning("Plotly unavailable: install plotly for charts.")
        chart_cols[1].warning("Plotly unavailable: install plotly for charts.")

    st.markdown("---")

    theme_map = get_theme_keyword_map()
    top_positive = _top_themes(df, theme_map, positive=True, top_n=4)
    top_concerns = _top_themes(df, theme_map, positive=False, top_n=4)
    recommendations = _aggregate_recommendations(df, theme_map, fallback=True)

    st.subheader("🏆 Top Positive Themes")
    if top_positive:
        for theme in top_positive:
            st.markdown(f"- {theme}")
    else:
        st.info("No positive themes detected yet.")

    st.markdown("---")
    st.subheader("⚠️ Common Student Concerns")
    if top_concerns:
        for theme in top_concerns:
            st.markdown(f"- {theme}")
    else:
        st.info("No common concerns have been detected yet.")

    st.markdown("---")
    st.subheader("💡 AI Recommendations")
    if recommendations:
        for rec in recommendations:
            st.markdown(f"- {rec}")
    else:
        st.info("No AI recommendations available yet.")

    st.markdown("---")
    st.subheader("📄 Recent Student Feedback")
    recent = df.sort_values(by="ID", ascending=False).head(10)
    cols = [c for c in recent.columns if c in ["Student", "Rating", "Sentiment", "Feedback"]]
    st.dataframe(recent[cols])
