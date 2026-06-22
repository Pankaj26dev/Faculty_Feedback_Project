import streamlit as st
from database.db import insert_feedback

st.set_page_config(
    page_title="Student Feedback",
    page_icon="📝",
    layout="centered"
)

st.title("Student Feedback Form")

faculty_name = st.text_input(
    "Faculty Name"
)

subject = st.text_input(
    "Subject"
)

rating = st.selectbox(
    "Rating",
    [1, 2, 3, 4, 5]
)

feedback_text = st.text_area(
    "Feedback",
    height=150
)

submit = st.button("Submit Feedback")

if submit:
    # Basic validation
    errors = []
    if not faculty_name or not faculty_name.strip():
        errors.append("Please enter the faculty name.")
    if not subject or not subject.strip():
        errors.append("Please enter the subject.")
    if not feedback_text or not feedback_text.strip():
        errors.append("Please provide feedback text.")

    if errors:
        for e in errors:
            st.error(e)
    else:
        try:
            # Ensure rating is an integer
            rating_value = int(rating)
            insert_feedback(
                faculty_name.strip(),
                subject.strip(),
                rating_value,
                feedback_text.strip(),
            )
            st.success("Feedback submitted successfully!")
            # Optionally clear the form inputs by reloading the page or
            # instructing the user to refresh. Streamlit doesn't provide a
            # simple programmatic way to clear text_input values here.
        except Exception as exc:
            st.error(f"An error occurred while saving feedback: {exc}")