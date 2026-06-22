import streamlit as st
import sqlite3
from database.db import insert_feedback, fetch_feedback, DB_NAME
from utils.ui import header, inject_css

st.set_page_config(page_title="Unfiltered", page_icon="🧾", layout="wide")


def get_faculty_list():
	conn = sqlite3.connect(DB_NAME)
	cur = conn.cursor()
	cur.execute("SELECT DISTINCT faculty_name FROM feedback ORDER BY faculty_name COLLATE NOCASE")
	rows = [r[0] for r in cur.fetchall() if r[0]]
	conn.close()
	return rows


def student_view():
	st.header("Student Feedback Form")
	faculties = get_faculty_list()
	with st.form(key="feedback_form"):
		student_name = st.text_input("Your name (optional)")
		faculty = st.selectbox("Select faculty", options=(faculties + ["Other"]) if faculties else ["Other"]) 
		if faculty == "Other":
			faculty = st.text_input("Enter faculty name")
		subject = st.text_input("Subject")
		rating = st.selectbox("Rating", [1,2,3,4,5])
		feedback_text = st.text_area("Feedback", height=150)
		submit = st.form_submit_button("Submit Feedback")
		if submit:
			if not faculty or not feedback_text.strip():
				st.error("Please provide faculty name and feedback text.")
			else:
				insert_feedback(faculty, subject, int(rating), feedback_text, student_name)
				st.success("Feedback submitted — thank you!")


def faculty_view():
	st.header("Faculty Review")
	faculties = get_faculty_list()
	if not faculties:
		st.info("No faculty entries yet.")
		return
	selected = st.selectbox("Select faculty to review", faculties)
	if selected:
		rows = fetch_feedback()
		# filter rows for selected faculty
		filtered = [r for r in rows if r[2] == selected]
		if not filtered:
			st.info("No feedback for selected faculty yet.")
			return
		import pandas as pd, json
		# Construct DataFrame similar to dashboard
		cols = ["ID","Student","Faculty","Subject","Rating","Feedback","Sentiment","Theme IDs","Recommendations","Theme Scores","Created At"]
		df = pd.DataFrame(filtered)
		# try to map columns (depends on DB schema)
		if df.shape[1] >= 11:
			df = df.iloc[:, :11]
			df.columns = cols[:df.shape[1]]
		else:
			# fallback simple mapping
			df.columns = [f"col_{i}" for i in range(df.shape[1])]

		st.subheader("Summary")
		total = len(df)
		avg = round(df['Rating'].astype(float).mean(),2) if 'Rating' in df.columns else 'N/A'
		st.metric("Total Feedback", total)
		st.metric("Average Rating", avg)

		st.subheader("Recent Feedback")
		st.dataframe(df[[c for c in df.columns if c in ['Student','Subject','Rating','Feedback','Sentiment','Recommendations']]].head(50))


def main():
	inject_css()
	header("Unfiltered", "AI-powered faculty insight and feedback analytics")
	st.write("#")
	c1, c2 = st.columns(2)
	with c1:
		if st.button("Student Feedback", key="nav_student"):
			st.session_state['view'] = 'student'
	with c2:
		if st.button("Faculty Review", key="nav_faculty"):
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