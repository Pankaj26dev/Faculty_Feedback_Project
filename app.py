import streamlit as st
import sqlite3
from database.db import insert_feedback, fetch_feedback, DB_NAME, get_all_faculty_subject_map
from utils.dashboard import render_faculty_dashboard
from utils.ui import header, inject_css

st.set_page_config(page_title="Unfiltered", page_icon="🧾", layout="wide")


def get_faculty_choices():
    faculty_map = get_all_faculty_subject_map()
    return [f"{name} ({subject})" for name, subject in sorted(faculty_map.items(), key=lambda item: item[0].lower())]


def student_view():
    st.header("Student Feedback Form")
    faculty_map = get_all_faculty_subject_map()
    faculty_choices = get_faculty_choices()
    faculty_choices.append("Add new faculty")

    with st.form(key="feedback_form"):
        student_name = st.text_input("Your name (optional)")
        faculty_choice = st.selectbox("Select faculty", faculty_choices)

        if faculty_choice == "Add new faculty":
            faculty = st.text_input("Faculty name")
            subject = st.text_input("Subject")
        else:
            faculty, subject = faculty_choice.rsplit(" (", 1)
            subject = subject.rstrip(")")
            st.markdown(f"**Subject:** {subject}")

        rating = st.selectbox("Rating", [1, 2, 3, 4, 5])
        feedback_text = st.text_area("Feedback", height=150)
        submit = st.form_submit_button("Submit Feedback")

        if submit:
            errors = []
            if not faculty or not faculty.strip():
                errors.append("Please provide a faculty name.")
            if not subject or not subject.strip():
                errors.append("Please provide a subject for this faculty.")
            if not feedback_text or not feedback_text.strip():
                errors.append("Please provide feedback text.")

            if errors:
                for e in errors:
                    st.error(e)
            else:
                insert_feedback(faculty.strip(), subject.strip(), int(rating), feedback_text.strip(), student_name.strip())
                st.success("Feedback submitted — thank you!")


def faculty_view():
    render_faculty_dashboard()


def main():
	inject_css()
	header("Unfiltered", "AI-powered faculty insight and feedback analytics")
	st.write("#")
	c1, c2 = st.columns(2)
	with c1:
		if st.button("Student Feedback", key="nav_student"):
			# If the project uses Streamlit multipage, navigate to the Student page.
			try:
				st.experimental_set_query_params(page="Student Feedback")
				st.experimental_rerun()
			except Exception:
				st.session_state['view'] = 'student'
	with c2:
		if st.button("Faculty Review", key="nav_faculty"):
			# Try to navigate to the multipage "Faculty Dashboard" if available,
			# otherwise fall back to the in-app faculty view.
			try:
				st.experimental_set_query_params(page="Faculty Dashboard")
				st.experimental_rerun()
			except Exception:
				st.session_state['view'] = 'faculty'

	view = st.session_state.get('view', 'home')
	if view == 'student':
		student_view()
	elif view == 'faculty':
		faculty_view()
	else:
		st.markdown("""
		### Welcome to Unfiltered

		Choose an option above to begin.
		""")


if __name__ == '__main__':
	if 'view' not in st.session_state:
		st.session_state['view'] = 'home'
	main()