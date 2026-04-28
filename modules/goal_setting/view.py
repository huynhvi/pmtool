import streamlit as st
import plotly.express as px
import pandas as pd
from . import loader, metrics, dept_loader
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


def render_sidebar():
    """Render Goal Setting sidebar filters. Must be called OUTSIDE any tab context."""
    df = loader.load_goal_data()
    if df is None:
        return

    goal_depts = sorted(df["Phòng ban"].unique().tolist())
    approver_options = sorted(df["Người duyệt"].unique().tolist())
    raw_statuses = sorted(df["Trạng thái"].unique().tolist())
    status_display_options = [_STATUS_LABEL_MAP.get(s, s) for s in raw_statuses]

    _dept_df = dept_loader.load_department_df()
    _filter_options, _, _ = dept_loader.build_filter_options(_dept_df, goal_depts)

    with st.sidebar:
        st.header("Goal Setting Filters")
        st.multiselect("Department", _filter_options, key="gs_dept")
        st.multiselect("Approver", approver_options, key="gs_approver")
        st.multiselect("Status", status_display_options, key="gs_status")


def render():
    df = loader.load_goal_data()
    if df is None:
        st.info("No data available yet. Ask your Admin to upload and process the Goal Setting file.")
        return

    goal_depts = sorted(df["Phòng ban"].unique().tolist())
    _dept_df = dept_loader.load_department_df()
    _filter_options, _display_to_name, _children_by_name = dept_loader.build_filter_options(
        _dept_df, goal_depts
    )
    _dept_name_to_group = dept_loader.build_dept_name_to_group(_dept_df)

    dept_labels  = st.session_state.get("gs_dept", [])
    approver     = st.session_state.get("gs_approver", [])
    status_labels = st.session_state.get("gs_status", [])

    selected_dept_names = [_display_to_name.get(l, l) for l in dept_labels]
    expanded_depts = sorted(dept_loader.get_all_descendant_names(selected_dept_names, _children_by_name))

    status_raw = [_STATUS_LABEL_MAP_INV.get(s, s) for s in status_labels]
    df = metrics.apply_filters(df, expanded_depts, approver, status_raw)
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

    render_section_header("Dept Group Comparison")
    dg_comp_df = metrics.compute_dept_group_comparison(df, _dept_name_to_group)

    col_dg_bar, col_dg_stack = st.columns(2)

    with col_dg_bar:
        dg_sorted = dg_comp_df.sort_values("Completion%", ascending=True)
        dg_bar = px.bar(
            dg_sorted,
            x="Completion%", y="Department Group", orientation="h",
            color_discrete_sequence=["#8B5CF6"],
            text=dg_sorted.apply(
                lambda r: f"{int(r['Completed'])} / {int(r['Total'])} ({r['Completion%']:.1f}%)", axis=1
            ),
        )
        dg_bar = make_chart_fig(dg_bar, "Completion % by Dept Group")
        dg_bar.update_layout(showlegend=False, yaxis_title="", xaxis_title="Completion %")
        st.plotly_chart(dg_bar, use_container_width=True)

    with col_dg_stack:
        dg_base = dg_comp_df.sort_values("Completion%", ascending=True)
        dg_stacked = dg_base.melt(
            id_vars=["Department Group", "Total"],
            value_vars=["Completed", "In Progress", "Not Started"],
            var_name="Status", value_name="Count",
        )
        dg_stacked["label"] = dg_stacked.apply(
            lambda r: f"{int(r['Count'])} ({r['Count'] / r['Total'] * 100:.1f}%)" if r["Count"] > 0 else "",
            axis=1,
        )
        dg_stacked_fig = px.bar(
            dg_stacked,
            x="Count", y="Department Group", orientation="h",
            color="Status", color_discrete_map=STATUS_COLORS,
            barmode="stack", text="label",
        )
        dg_stacked_fig.update_traces(textposition="inside", insidetextanchor="middle")
        dg_stacked_fig = make_chart_fig(dg_stacked_fig, "Status Breakdown by Dept Group")
        dg_stacked_fig.update_layout(yaxis_title="", xaxis_title="Count")
        st.plotly_chart(dg_stacked_fig, use_container_width=True)

    st.markdown('<hr class="pm-divider">', unsafe_allow_html=True)

    render_section_header("Department Detail Comparison")
    dept_comp_df = metrics.compute_department_comparison(df)

    col_comp_bar, col_comp_stack = st.columns(2)

    with col_comp_bar:
        comp_sorted = dept_comp_df.sort_values("Completion%", ascending=True)
        bar_comp = px.bar(
            comp_sorted,
            x="Completion%", y="Department", orientation="h",
            color_discrete_sequence=["#3B82F6"],
            text=comp_sorted.apply(
                lambda r: f"{int(r['Completed'])} / {int(r['Total'])} ({r['Completion%']:.1f}%)", axis=1
            ),
        )
        bar_comp = make_chart_fig(bar_comp, "Completion % by Department")
        bar_comp.update_layout(showlegend=False, yaxis_title="", xaxis_title="Completion %")
        st.plotly_chart(bar_comp, use_container_width=True)

    with col_comp_stack:
        comp_base = dept_comp_df.sort_values("Completion%", ascending=True)
        stacked_df = comp_base.melt(
            id_vars=["Department", "Total"],
            value_vars=["Completed", "In Progress", "Not Started"],
            var_name="Status", value_name="Count",
        )
        stacked_df["label"] = stacked_df.apply(
            lambda r: f"{int(r['Count'])} ({r['Count'] / r['Total'] * 100:.1f}%)" if r["Count"] > 0 else "",
            axis=1,
        )
        stacked_fig = px.bar(
            stacked_df,
            x="Count", y="Department", orientation="h",
            color="Status", color_discrete_map=STATUS_COLORS,
            barmode="stack", text="label",
        )
        stacked_fig.update_traces(textposition="inside", insidetextanchor="middle")
        stacked_fig = make_chart_fig(stacked_fig, "Status Breakdown by Department")
        stacked_fig.update_layout(yaxis_title="", xaxis_title="Count")
        st.plotly_chart(stacked_fig, use_container_width=True)

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
