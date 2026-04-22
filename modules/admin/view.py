import streamlit as st
from modules.goal_setting import processor as gs_processor
from modules.issue_tracking import processor as it_processor
from config import GOAL_SETTING_DATA, ISSUE_SNAPSHOTS_DIR, ISSUE_SNAPSHOTS_CLOUD_PREFIX
from utils.ui_helpers import render_section_header
from utils import storage


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
    mode = "☁ Cloud (Supabase)" if storage._use_cloud() else "💾 Local"
    st.caption(f"{mode} | {storage.snapshot_info(ISSUE_SNAPSHOTS_CLOUD_PREFIX, ISSUE_SNAPSHOTS_DIR)}")
    with st.expander("🔧 Debug: snapshot storage", expanded=False):
        files = storage.list_files(ISSUE_SNAPSHOTS_CLOUD_PREFIX, ISSUE_SNAPSHOTS_DIR)
        st.write(f"**Files found:** {files}")
        if storage._use_cloud():
            try:
                raw = storage._supabase().storage.from_(storage.BUCKET).list("")
                st.write(f"**Raw bucket listing:** {raw}")
            except Exception as e:
                st.write(f"**Listing error:** {e}")

    it_file = st.file_uploader(
        "Upload Raw Issue Tracking Excel (.xlsx)", type=["xlsx"], key="admin_it_upload"
    )
    if it_file is not None:
        if st.button("Process & Save — Issue Tracking", type="primary", key="admin_it_btn"):
            with st.spinner("Generating snapshot..."):
                result = it_processor.process_and_save(it_file)
            if result["success"]:
                st.success(result["message"] + " Dashboard updated.")
                st.rerun()
            else:
                st.error(result["message"])
