import streamlit as st
from database.db import insert_feedback, get_all_faculty_subject_map

st.set_page_config(
    page_title="Student Feedback",
    page_icon="📝",
    layout="centered"
)

st.title("Student Feedback Form")

faculty_map = get_all_faculty_subject_map()
faculty_choices = [f"{name} ({subject})" for name, subject in sorted(faculty_map.items(), key=lambda item: item[0].lower())]
faculty_choices.append("Add new faculty")

with st.form(key="feedback_form"):
    student_name = st.text_input("Your name (optional)")
    faculty_choice = st.selectbox("Select faculty", faculty_choices)

    if faculty_choice == "Add new faculty":
        faculty_name = st.text_input("Faculty name")
        subject = st.text_input("Subject")
    else:
        faculty_name, subject = faculty_choice.rsplit(" (", 1)
        subject = subject.rstrip(")")
        st.markdown(f"**Subject:** {subject}")

    rating = st.selectbox("Rating", [1, 2, 3, 4, 5])
    feedback_text = st.text_area("Feedback", height=150)
    submit = st.form_submit_button("Submit Feedback")

    if submit:
        errors = []
        if not faculty_name or not faculty_name.strip():
            errors.append("Please enter the faculty name.")
        if not subject or not subject.strip():
            errors.append("Please provide or confirm the subject.")
        if not feedback_text or not feedback_text.strip():
            errors.append("Please provide feedback text.")

        if errors:
            for e in errors:
                st.error(e)
        else:
            try:
                rating_value = int(rating)
                insert_feedback(
                    faculty_name.strip(),
                    subject.strip(),
                    rating_value,
                    feedback_text.strip(),
                    student_name.strip(),
                )
                st.success("Feedback submitted successfully!")
            except Exception as exc:
                st.error(f"An error occurred while saving feedback: {exc}")