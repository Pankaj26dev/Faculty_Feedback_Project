import streamlit as st

CSS = """
<style>
/* Page background and card styling */
body {background-color: #f7fafc;}
.header-card {
  background: linear-gradient(90deg, #4f46e5, #06b6d4);
  color: white;
  padding: 22px 24px;
  border-radius: 14px;
  box-shadow: 0 18px 40px rgba(15, 23, 42, 0.13);
}
.dashboard-card {
  background: white;
  padding: 18px;
  border-radius: 16px;
  box-shadow: 0 12px 30px rgba(15, 23, 42, 0.08);
  margin-bottom: 16px;
}
.section-header {
  font-size: 1.05rem;
  font-weight: 700;
  color: #111827;
  margin-bottom: 10px;
}
.recommendation-card {
  border-left: 4px solid #2563eb;
  background: #eff6ff;
  padding: 16px 18px;
  border-radius: 12px;
  margin-bottom: 12px;
}
.feedback-card {
  border-left: 4px solid #16a34a;
  background: #ecfdf5;
  padding: 16px 18px;
  border-radius: 12px;
  margin-bottom: 12px;
}
.small-note {
  color: #475569;
  font-size: 0.94rem;
  line-height: 1.5;
}
.button-card {
  background: #1f2937;
  color: white;
  padding: 16px 18px;
  border-radius: 12px;
}
.muted {
  color: #64748b;
}
</style>
"""


def inject_css():
    st.markdown(CSS, unsafe_allow_html=True)


def header(title: str, subtitle: str = None):
    inject_css()
    st.markdown(f"""
    <div class="header-card">
      <h1 style="margin:0">{title}</h1>
      <div class="muted">{subtitle or ''}</div>
    </div>
    """, unsafe_allow_html=True)


def big_buttons(col1_label: str, col2_label: str):
    c1, c2, _ = st.columns([1,1,2])
    with c1:
        if st.button(col1_label, key="big1"):
            return 'left'
    with c2:
        if st.button(col2_label, key="big2"):
            return 'right'
    return None
