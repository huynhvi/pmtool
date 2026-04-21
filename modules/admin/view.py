import streamlit as st
from modules.goal_setting import processor as gs_processor
from modules.issue_tracking import processor as it_processor
from config import GOAL_SETTING_DATA, ISSUE_TRACKING_DATA
from utils.ui_helpers import render_section_header
from utils import storage

_CONFIDENCE_ICON = {"high": "✅", "medium": "⚠️", "low": "❌", "none": "❌"}


def render():
    render_section_header("Admin Panel — Data Processing")

    st.markdown('<hr class="pm-divider">', unsafe_allow_html=True)

    # ── Goal Setting ─────────────────────────────────────────────────
    st.subheader("Goal Setting Data")
    st.caption(storage.file_info("goal_setting_processed.json", GOAL_SETTING_DATA))

    gs_file = st.file_uploader(
        "Upload Raw Goal Setting Excel (.xlsx)", type=["xlsx"], key="admin_gs_upload"
    )
    if gs_file is not None:
        if st.button("Process & Save — Goal Setting", type="primary", key="admin_gs_btn"):
            with st.spinner("Processing Goal Setting data..."):
                result = gs_processor.process_and_save(gs_file)
            if result["success"]:
                st.success(result["message"] + " Dashboard updated.")
                st.rerun()
            else:
                st.error(result["message"])

    st.markdown('<hr class="pm-divider">', unsafe_allow_html=True)

    # ── Issue Tracking ───────────────────────────────────────────────
    st.subheader("Issue Tracking Data")
    st.caption(storage.file_info("issue_tracking_processed.json", ISSUE_TRACKING_DATA))

    it_file = st.file_uploader(
        "Upload Raw Issue Tracking Excel (.xlsx)", type=["xlsx"], key="admin_it_upload"
    )
    if it_file is not None:
        if st.button("Process & Save — Issue Tracking", type="primary", key="admin_it_btn"):
            with st.spinner("Analyzing file structure with AI..."):
                result = it_processor.process_and_save(it_file)
            if result["success"]:
                st.success(result["message"] + " Dashboard updated.")
                mapping = result.get("mapping", {})
                if mapping:
                    st.caption("AI Column Mapping Result:")
                    cols = st.columns(len(mapping))
                    for i, (field, m) in enumerate(mapping.items()):
                        icon = _CONFIDENCE_ICON.get(m.get("confidence", "none"), "❌")
                        detected = m.get("column") or "—"
                        cols[i].metric(field, detected, icon)
                st.rerun()
            else:
                st.error(result["message"])
