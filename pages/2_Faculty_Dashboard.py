import streamlit as st
import pandas as pd

from database.db import fetch_feedback

st.title("Faculty Dashboard")

data = fetch_feedback()

# Handle databases with either 6 or 7 columns (some rows may lack `created_at`).
if data:
    first_row = data[0]
    if len(first_row) == 7:
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

st.subheader("All Feedback")

st.dataframe(df)
