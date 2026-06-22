import streamlit as st
import pandas as pd

from database.db import fetch_feedback

st.title("Faculty Dashboard")

data = fetch_feedback()

# Handle different DB schemas. Prefer newer schema with stored recommendations.
if data:
    first_row = data[0]
    # newer schema includes theme_ids, recommendations, theme_scores (+ created_at)
    if len(first_row) >= 9:
        columns = [
            "ID",
            "Faculty Name",
            "Subject",
            "Rating",
            "Feedback",
            "Sentiment",
            "Theme IDs",
            "Recommendations",
            "Theme Scores",
        ]
        # handle any extra trailing columns (e.g., created_at)
        if len(first_row) > len(columns):
            for i in range(len(columns), len(first_row)):
                columns.append(f"col_{i}")
    elif len(first_row) == 7:
        columns = [
            "ID",
            "Faculty Name",
            "Subject",
            "Rating",
            "Feedback",
            "Sentiment",
            "Created At",
        ]
    elif len(first_row) == 6:
        columns = [
            "ID",
            "Faculty Name",
            "Subject",
            "Rating",
            "Feedback",
            "Sentiment",
        ]
    else:
        columns = [f"col_{i}" for i in range(len(first_row))]
    df = pd.DataFrame(data, columns=columns)
else:
    df = pd.DataFrame(columns=["ID", "Faculty Name", "Subject", "Rating", "Feedback", "Sentiment", "Created At"])
total_feedback = len(df)

if total_feedback == 0:
    st.warning("No feedback records are available yet.")
else:
    average_rating = round(df["Rating"].mean(), 2)
    sentiment_counts = df["Sentiment"].value_counts().to_dict()

    positive_count = sentiment_counts.get("Positive", 0)
    neutral_count = sentiment_counts.get("Neutral", 0)
    negative_count = sentiment_counts.get("Negative", 0)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(label="Total Feedback", value=total_feedback)
    with col2:
        st.metric(label="Average Rating", value=average_rating)
    with col3:
        st.metric(label="Positive Feedback", value=positive_count)

    col4, col5 = st.columns(2)

    with col4:
        st.metric(label="Neutral Feedback", value=neutral_count)
    with col5:
        st.metric(label="Negative Feedback", value=negative_count)

    # Sentiment distribution charts
    try:
        import plotly.express as px

        sent_series = df["Sentiment"].value_counts().reset_index()
        sent_series.columns = ["Sentiment", "Count"]

        fig_pie = px.pie(sent_series, names="Sentiment", values="Count", title="Sentiment Distribution")
        st.plotly_chart(fig_pie, use_container_width=True)

        fig_bar = px.bar(sent_series.sort_values("Count", ascending=False), x="Sentiment", y="Count", title="Sentiment Counts")
        st.plotly_chart(fig_bar, use_container_width=True)
    except Exception as e:
        st.warning(f"Plotly chart unavailable: {e}")

    # Recommendations: prefer stored recommendations if available
    import json

    if "Recommendations" in df.columns:
        def _parse_stored(r):
            try:
                if r is None:
                    return ""
                if isinstance(r, str) and r.strip() == "":
                    return ""
                recs = json.loads(r) if isinstance(r, str) else r
                if not recs:
                    return ""
                return " | ".join(recs)
            except Exception:
                return str(r)

        df["Recommendations"] = df["Recommendations"].apply(_parse_stored)
        st.subheader("Recommendations (stored)")
        st.dataframe(df)
    else:
        st.info("No stored recommendations found in the database.")

    # Allow on-demand recompute (in-memory) if user requests it
    try:
        if st.checkbox("Recompute recommendations on demand (may be slow)"):
            with st.spinner("Loading model and computing recommendations..."):
                from ai.knowledge_base import get_theme_keyword_map
                from ai.semantic_analysis import load_model, build_theme_embeddings, detect_themes

                theme_map = get_theme_keyword_map()
                model = load_model()
                theme_ids, theme_embs = build_theme_embeddings(theme_map, model)

                recs_list = []
                for feedback in df["Feedback"]:
                    try:
                        matches = detect_themes(feedback, theme_ids, theme_embs, model, top_k=3, min_score=0.35)
                        if matches:
                            combined = " | ".join([f"{tid}: {theme_map[tid]['theme_name']}" for tid, score in matches])
                        else:
                            combined = ""
                    except Exception as e:
                        combined = f"Error: {e}"
                    recs_list.append(combined)

                df["Recomputed Recommendations"] = recs_list
                st.subheader("Recomputed Recommendations (in-memory)")
                st.dataframe(df)
    except Exception:
        st.info("Recommendation engine not available. Install `sentence-transformers` to enable recompute.")

st.subheader("All Feedback")

st.dataframe(df)
