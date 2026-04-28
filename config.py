import os

COMPLETED_STATUSES = ["E_APPROVED"]
NOT_STARTED_STATUS = "E_WAITING_HANDLING"
SNAPSHOT_WINDOW = 5
LOW_COMPLETION_THRESHOLD = 50.0

def _load_accounts():
    try:
        import streamlit as st
        if "accounts" in st.secrets:
            return {name: {"password": creds["password"], "role": creds["role"]}
                    for name, creds in st.secrets["accounts"].items()}
    except Exception:
        pass
    return {
        "Admins": {"password": "Admin@41+", "role": "admin"},
        "Usr":    {"password": "123456",    "role": "user"},
    }

ACCOUNTS = _load_accounts()

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
GOAL_SETTING_DATA          = os.path.join(DATA_DIR, "goal_setting_processed.json")
ISSUE_TRACKING_DATA        = os.path.join(DATA_DIR, "issue_tracking_processed.json")
ISSUE_SNAPSHOTS_DIR         = os.path.join(DATA_DIR, "issue_snapshots")
ISSUE_SNAPSHOTS_CLOUD_PREFIX = "snapshot_"   # root-level prefix in Supabase bucket

DEPARTMENT_DATA = os.path.join(os.path.dirname(__file__), "Dashboard", "Department", "vngg_department_updated 28Apr26.xlsx")
