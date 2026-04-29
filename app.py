import streamlit as st
import auth
from modules.goal_setting import view as goal_view
from modules.issue_tracking import view as issue_view
from modules.admin import view as admin_view
from utils.ui_helpers import inject_css

st.set_page_config(
    page_title="PMTool Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_css()

if not st.session_state.get("authenticated"):
    auth.render_login()
    st.stop()

with st.sidebar:
    auth.render_logout_button()
    st.caption("build: v2.2 — 2026-04-29")

goal_view.render_sidebar()

role = st.session_state.get("role", "user")

if role == "admin":
    tab_admin, tab1, tab2 = st.tabs(["⚙ Admin", "📋  Goal Setting", "🐛  Issue Tracking"])
    with tab_admin:
        admin_view.render()
    with tab1:
        goal_view.render()
    with tab2:
        issue_view.render()
else:
    tab1, tab2 = st.tabs(["📋  Goal Setting", "🐛  Issue Tracking"])
    with tab1:
        goal_view.render()
    with tab2:
        issue_view.render()
