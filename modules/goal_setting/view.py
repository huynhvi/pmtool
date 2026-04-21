import streamlit as st
import plotly.express as px
import pandas as pd
from . import loader, metrics
from utils.ui_helpers import (
    render_kpi_cards, render_section_header, make_chart_fig,
    style_completion_table, STATUS_COLORS,
)
from config import LOW_COMPLETION_THRESHOLD

_STATUS_LABEL_MAP = {
    "E_ADJUST":           "Awaiting Adjustment",
    "E_APPROVED":         "Approved",
    "E_WAITING_APPROVE":  "Awaiting Approval",
    "E_WAITING_HANDLING": "Awaiting Action",
}
_STATUS_LABEL_MAP_INV = {v: k for k, v in _STATUS_LABEL_MAP.items()}


def render():
    df = loader.load_goal_data()
    if df is None:
        st.info("No data available yet. Ask your Admin to upload and process the Goal Setting file.")
        return

    dept_options = sorted(df["Phòng ban"].unique().tolist())
    approver_options = sorted(df["Người duyệt"].unique().tolist())
    raw_statuses = sorted(df["Trạng thái"].unique().tolist())
    status_display_options = [_STATUS_LABEL_MAP.get(s, s) for s in raw_statuses]

    with st.sidebar:
        st.header("Goal Setting Filters")
        dept = st.multiselect("Department", dept_options, key="gs_dept")
        approver = st.multiselect("Approver", approver_options, key="gs_approver")
        status_labels = st.multiselect("Status", status_display_options, key="gs_status")

    status_raw = [_STATUS_LABEL_MAP_INV.get(s, s) for s in status_labels]
    df = metrics.apply_filters(df, dept, approver, status_raw)
    kpis = metrics.compute_kpis(df)

    # ── TOP: KPI cards ──────────────────────────────────────────────
    render_section_header("Summary")
    render_kpi_cards([
        {"label": "Total Goal Sheets", "value": kpis["total"],       "color": "gray"},
        {"label": "Completed",         "value": kpis["completed"],   "color": "green"},
        {"label": "In Progress",       "value": kpis["in_progress"], "color": "yellow"},
        {"label": "Not Started",       "value": kpis["not_started"], "color": "red"},
    ])

    st.markdown('<hr class="pm-divider">', unsafe_allow_html=True)

    # ── MIDDLE: Charts ──────────────────────────────────────────────
    render_section_header("Overview")
    col_chart1, col_chart2 = st.columns([1.15, 0.85])

    with col_chart1:
        status_df = metrics.compute_status_distribution(df)
        status_df["Status"] = status_df["Status"].replace(_STATUS_LABEL_MAP)
        bar_fig = px.bar(
            status_df, x="Count", y="Status", orientation="h",
            color="Status", color_discrete_map=STATUS_COLORS,
            text="Count",
        )
        bar_fig = make_chart_fig(bar_fig, "Goal Sheet Status Distribution")
        bar_fig.update_layout(showlegend=False, yaxis_title="", xaxis_title="Count")
        st.plotly_chart(bar_fig, use_container_width=True)

    with col_chart2:
        pie_data = pd.DataFrame({
            "Category": ["Completed", "In Progress", "Not Started"],
            "Count":    [kpis["completed"], kpis["in_progress"], kpis["not_started"]],
        })
        pie_fig = px.pie(
            pie_data, names="Category", values="Count", hole=0.45,
            color="Category", color_discrete_map=STATUS_COLORS,
        )
        pie_fig = make_chart_fig(pie_fig, "Completion Proportion")
        st.plotly_chart(pie_fig, use_container_width=True)

    st.markdown('<hr class="pm-divider">', unsafe_allow_html=True)

    # ── BOTTOM: Tables ──────────────────────────────────────────────
    render_section_header("Detailed Breakdown")
    col_left, col_right = st.columns(2)

    with col_left:
        st.caption("Department Progress")
        dept_df = metrics.compute_department_progress(df)
        styled_dept = style_completion_table(dept_df, rules=[
            {"col": "Completion%", "op": "lt", "threshold": LOW_COMPLETION_THRESHOLD, "color": "#FEF2F2"},
        ]).format({"Completion%": "{:.2f}%"})
        st.dataframe(styled_dept, use_container_width=True, hide_index=True)

    with col_right:
        st.caption("Approver Workload")
        approver_df = metrics.compute_approver_workload(df)
        avg_pending = float(approver_df["Pending"].mean()) if len(approver_df) > 0 else 0
        styled_approver = style_completion_table(approver_df, rules=[
            {"col": "Pending",     "op": "gt", "threshold": avg_pending,            "color": "#FFFBEB"},
            {"col": "Completion%", "op": "lt", "threshold": LOW_COMPLETION_THRESHOLD, "color": "#FEF2F2"},
        ]).format({"Completion%": "{:.2f}%"})
        st.dataframe(styled_approver, use_container_width=True, hide_index=True)

    st.markdown('<hr class="pm-divider">', unsafe_allow_html=True)

    render_section_header("Follow-up Required")
    followup_df = metrics.get_followup_list(df)
    count = len(followup_df)
    if count > 0:
        st.markdown(
            f'<span style="background:#FEF2F2;color:#DC2626;padding:.2rem .65rem;'
            f'border-radius:999px;font-size:.8rem;font-weight:700;">⚠ {count} require follow-up</span>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<span style="background:#F0FDF4;color:#16A34A;padding:.2rem .65rem;'
            'border-radius:999px;font-size:.8rem;font-weight:700;">✓ No follow-up needed</span>',
            unsafe_allow_html=True,
        )
    st.dataframe(followup_df, use_container_width=True, hide_index=True)
