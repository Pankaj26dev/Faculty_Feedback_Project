import json
from collections import Counter
from typing import Dict, List, Tuple

import pandas as pd
import streamlit as st

from ai.knowledge_base import get_theme_keyword_map
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


def _render_metric_card(title: str, value: str, caption: str):
    st.markdown(
        f"""
        <div class='dashboard-card'>
            <div class='section-header'>{title}</div>
            <div style='font-size:2rem; font-weight:700; margin-bottom: 8px;'>{value}</div>
            <div class='small-note'>{caption}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _aggregate_recommendations(df: pd.DataFrame, theme_map: Dict[str, Dict]) -> List[str]:
    generic_terms = {"Average / Neutral Feedback", "Mixed: Good Knowledge, Poor Delivery", "No Specific Feedback", "General"}
    recs = []

    if "Recommendations" in df.columns:
        for raw in df["Recommendations"]:
            for value in _safe_json_load(raw):
                if isinstance(value, str):
                    val = value.strip()
                    if val and val not in generic_terms:
                        recs.append(val)
    if recs:
        return list(dict.fromkeys(recs))[:8]

    if "Theme IDs" in df.columns:
        all_ids = []
        for raw in df["Theme IDs"]:
            all_ids.extend(_safe_json_load(raw))
        counts = Counter(all_ids)
        recs = []
        for tid, _ in counts.most_common(8):
            info = theme_map.get(tid, {})
            rec = info.get("recommendation") or info.get("theme_name", tid)
            if rec and rec not in generic_terms and rec not in recs:
                recs.append(rec)
        if recs:
            return recs

    return []


def _top_themes(df: pd.DataFrame, theme_map: Dict[str, Dict], positive: bool = True, top_n: int = 4) -> List[str]:
    generic_terms = {"Average / Neutral Feedback", "Mixed: Good Knowledge, Poor Delivery", "No Specific Feedback", "General"}

    if "Theme IDs" in df.columns:
        theme_ids = []
        for raw in df["Theme IDs"]:
            theme_ids.extend(_safe_json_load(raw))
        if theme_ids:
            counts = Counter(theme_ids)
            filtered_ids = []
            for tid, _ in counts.most_common():
                info = theme_map.get(tid, {})
                sentiment = str(info.get("sentiment", "")).lower()
                if positive and sentiment == "positive":
                    filtered_ids.append(tid)
                elif not positive and sentiment == "negative":
                    filtered_ids.append(tid)

            if not filtered_ids:
                filtered_ids = [tid for tid, _ in counts.most_common()]

            names = [theme_map.get(tid, {}).get("theme_name", tid) for tid in filtered_ids[:top_n]]
            return [n for n in names if n not in generic_terms][:top_n]

    return []


def render_faculty_dashboard():
    st.title("Unfiltered: Faculty Insight & Feedback Analytics")
    st.sidebar.title("Faculty dashboard filters")
    min_rating = st.sidebar.slider("Minimum rating", 1, 5, 1)
    sentiment_filter = st.sidebar.multiselect(
        "Include sentiment",
        ["Positive", "Neutral", "Negative"],
        default=["Positive", "Neutral", "Negative"],
    )
    show_recent = st.sidebar.checkbox("Show recent feedback", value=True)

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
    if "Faculty" in df.columns:
        df = df[df["Faculty"] == selected]

    if "Rating" in df.columns:
        df = df[df["Rating"] >= min_rating]

    if "Sentiment" in df.columns and sentiment_filter:
        df = df[df["Sentiment"].isin(sentiment_filter)]

    if df.empty:
        st.warning(f"No feedback matches the current filters for {selected}.")
        return

    total_feedback = len(df)
    avg_rating = round(df["Rating"].mean(), 2) if "Rating" in df.columns else "N/A"
    sentiment_counts = df["Sentiment"].value_counts().to_dict() if "Sentiment" in df.columns else {}
    positive = sentiment_counts.get("Positive", 0)
    neutral = sentiment_counts.get("Neutral", 0)
    negative = sentiment_counts.get("Negative", 0)
    theme_map = get_theme_keyword_map()
    top_positive = _top_themes(df, theme_map, positive=True, top_n=4)
    top_concerns = _top_themes(df, theme_map, positive=False, top_n=4)
    recommendations = _aggregate_recommendations(df, theme_map)

    st.markdown("---")
    cols = st.columns([2, 2, 2, 2])
    cols[0].markdown(f"**Faculty:** {selected}")
    cols[1].markdown(f"**Subject:** {subject}")
    cols[2].markdown(f"**Feedback Count:** {total_feedback}")
    cols[3].markdown(f"**Avg Rating:** {avg_rating}")
    st.markdown("---")

    detail_cols = st.columns(4)
    _render_metric_card("Positive comments", str(positive), "Number of feedback entries tagged positive.")
    _render_metric_card("Neutral comments", str(neutral), "Number of neutral or mixed feedback entries.")
    _render_metric_card("Negative comments", str(negative), "Number of feedback entries tagged negative.")
    unique_themes = 0
    if "Theme IDs" in df.columns:
        unique_themes = len({tid for raw in df["Theme IDs"] for tid in _safe_json_load(raw)})
    _render_metric_card("Theme insights", str(unique_themes), "Distinct themes identified in this faculty's feedback.")

    st.markdown("---")

    chart_cols = st.columns(2)
    try:
        import plotly.express as px

        if "Rating" in df.columns:
            rating_series = df["Rating"].value_counts().sort_index().reset_index()
            rating_series.columns = ["Rating", "Count"]
            fig_dist = px.bar(
                rating_series,
                x="Rating",
                y="Count",
                title="Rating distribution",
                labels={"Rating": "Rating", "Count": "Count"},
                template="plotly_white",
            )
            chart_cols[0].plotly_chart(fig_dist, use_container_width=True)
        else:
            chart_cols[0].info("Rating distribution is unavailable because rating data is missing.")

        if sentiment_counts:
            sentiment_series = pd.DataFrame(
                [(k, v) for k, v in sentiment_counts.items()], columns=["Sentiment", "Count"]
            )
            fig_sent = px.pie(
                sentiment_series,
                names="Sentiment",
                values="Count",
                title="Sentiment breakdown",
                template="plotly_white",
            )
            chart_cols[1].plotly_chart(fig_sent, use_container_width=True)
        else:
            chart_cols[1].info("Sentiment breakdown is unavailable because sentiment labels are missing.")
    except Exception:
        chart_cols[0].warning("Plotly unavailable: install plotly for charts.")
        chart_cols[1].warning("Plotly unavailable: install plotly for charts.")

    st.markdown("---")

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
    st.subheader("💡 Actionable Recommendations")
    st.markdown("Recommendations below are based on stored theme mappings and feedback insights.")
    if recommendations:
        for rec in recommendations:
            st.markdown(f"<div class='recommendation-card'>✅ {rec}</div>", unsafe_allow_html=True)
    else:
        st.info("No AI recommendations available yet. Submit more feedback or check theme extraction settings.")

    if show_recent:
        st.markdown("---")
        st.subheader("📄 Recent Student Feedback")
        recent = df.sort_values(by="ID", ascending=False).head(10)
        cols = [c for c in recent.columns if c in ["Student", "Rating", "Sentiment", "Feedback"]]
        if cols:
            st.dataframe(recent[cols])
        else:
            st.info("Recent feedback details are unavailable because required columns are missing.")
