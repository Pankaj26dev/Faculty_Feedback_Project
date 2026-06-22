import streamlit as st

CSS = """
<style>
/* Page background and card styling */
body {background-color: #f7fafc;}
.header-card {
  background: linear-gradient(90deg,#4f46e5,#06b6d4);
  color: white;
  padding: 18px;
  border-radius: 8px;
}
.big-button {
  display: inline-block;
  width: 220px;
  height: 80px;
  line-height: 80px;
  text-align: center;
  border-radius: 8px;
  background: #111827;
  color: white;
  font-size: 18px;
  margin: 8px;
  text-decoration: none;
}
.secondary-button {
  background: #10b981;
}
.muted {
  color: #6b7280;
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
