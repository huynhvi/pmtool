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
)

inject_css()

if not st.session_state.get("authenticated"):
    auth.render_login()
    st.stop()

with st.sidebar:
    auth.render_logout_button()
    st.caption("build: v2.1 — 2026-04-22")

st.markdown("""
<div style="width:100%;box-sizing:border-box;display:flex;align-items:center;gap:1rem;
    padding:.6rem 0 1.1rem 0;border-bottom:3px solid #2563EB;margin-bottom:1.1rem;">
  <span style="font-size:1.5rem;flex-shrink:0;">📊</span>
  <div style="flex:1;min-width:0;">
    <div style="font-size:1.35rem;font-weight:800;color:#111827;line-height:1.3;">PMTool Dashboard</div>
    <div style="font-size:0.75rem;color:#6B7280;margin-top:.1rem;">Project Management Monitoring System</div>
  </div>
</div>
""", unsafe_allow_html=True)

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
