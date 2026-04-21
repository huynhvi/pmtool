import streamlit as st
from config import ACCOUNTS


def check_login(account: str, password: str):
    user = ACCOUNTS.get(account)
    if user and user["password"] == password:
        return user["role"]
    return None


def render_login():
    st.markdown("""
<style>
[data-testid="stAppViewContainer"] { background: #F3F4F6; }
[data-testid="stAppViewContainer"] > .main { background: #F3F4F6; }
</style>
""", unsafe_allow_html=True)

    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        st.markdown("""
<div style="text-align:center;padding:2rem 0 1.2rem 0;">
  <div style="font-size:2.2rem;">📊</div>
  <div style="font-size:1.3rem;font-weight:800;color:#111827;margin-top:.3rem;">PMTool Dashboard</div>
  <div style="font-size:.75rem;color:#6B7280;margin-top:.2rem;">Project Management Monitoring System</div>
</div>
""", unsafe_allow_html=True)

        account = st.text_input("Account", placeholder="Enter your account", key="login_account")
        password = st.text_input("Password", placeholder="Enter your password",
                                 type="password", key="login_password")

        if st.button("Login", use_container_width=True, type="primary"):
            if not account.strip() or not password:
                st.error("Account and Password are required")
            else:
                role = check_login(account.strip(), password)
                if role is None:
                    st.error("Invalid account or password")
                else:
                    st.session_state["authenticated"] = True
                    st.session_state["role"] = role
                    st.session_state["account"] = account.strip()
                    st.rerun()


def render_logout_button():
    st.caption(f"Logged in as: **{st.session_state.get('account', '')}** ({st.session_state.get('role', '')})")
    if st.button("Logout", use_container_width=True):
        for key in ("authenticated", "role", "account"):
            st.session_state.pop(key, None)
        st.rerun()
