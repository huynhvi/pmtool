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
    # Not Started
    "E_WAITING_HANDLING":   "Not Started",
    "Chờ xử lý":            "Not Started",
    # In Progress
    "E_WAITING_APPROVE":    "Awaiting Approval",
    "Chờ duyệt":            "Awaiting Approval",
    "E_ADJUST":             "Awaiting Adjustment",
    "Yêu cầu điều chỉnh":   "Awaiting Adjustment",
    # Completed
    "E_APPROVED":           "Approved",
    "Đã duyệt":             "Approved",
    "Approved":             "Approved",
    "E_CANCELLED":          "Cancelled",
    "Hủy":                  "Cancelled",
    "Cancelled":            "Cancelled",
}


def _get_raw_statuses(display_labels: list) -> list:
    """Map display label(s) back to all matching raw status codes."""
    raw = []
    for label in display_labels:
        raw.extend(k for k, v in _STATUS_LABEL_MAP.items() if v == label)
    return raw


def render_sidebar():
    """Render Goal Setting sidebar filters. Must be called OUTSIDE any tab context."""
    df = loader.load_goal_data()
    if df is None:
        return

    goal_depts = sorted(df["Phòng ban"].dropna().unique().tolist())
    approver_options = sorted(df["Người duyệt"].dropna().unique().tolist())
    raw_statuses = sorted(df["Trạng thái"].dropna().unique().tolist())
    seen, status_display_options = set(), []
    for s in raw_statuses:
        label = _STATUS_LABEL_MAP.get(s, s)
        if label not in seen:
            status_display_options.append(label)
            seen.add(label)

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

    goal_depts = sorted(df["Phòng ban"].dropna().unique().tolist())
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

    status_raw = _get_raw_statuses(status_labels)
    df = metrics.apply_filters(df, expanded_depts, approver, status_raw)
    excluded_count = len(df) - len(metrics.get_effective_df(df))
    eff_df = metrics.get_effective_df(df)
    kpis = metrics.compute_kpis(eff_df)

    raw_total = len(df)
    excluded_pct = round(excluded_count / raw_total * 100, 2) if raw_total > 0 else 0.0

    # ── TOP: KPI cards ──────────────────────────────────────────────
    render_section_header("Summary")
    render_kpi_cards([
        {"label": "Total Goal Sheets",    "value": kpis["total"],       "color": "gray"},
        {"label": "Completed",            "value": kpis["completed"],   "color": "green",
         "subtitle": f"{kpis['completed_pct']:.2f}% of effective total"},
        {"label": "In Progress",          "value": kpis["in_progress"], "color": "yellow",
         "subtitle": f"{kpis['in_progress_pct']:.2f}% of effective total"},
        {"label": "Not Started",          "value": kpis["not_started"], "color": "red",
         "subtitle": f"{kpis['not_started_pct']:.2f}% of effective total"},
        {"label": "Excluded Goal Sheets", "value": excluded_count,      "color": "gray",
         "subtitle": f"{excluded_pct:.2f}% of raw total"},
    ])

    st.markdown('<hr class="pm-divider">', unsafe_allow_html=True)

    # ── MIDDLE: Charts ──────────────────────────────────────────────
    render_section_header("Overview")
    col_chart1, col_chart2 = st.columns([1.15, 0.85])

    with col_chart1:
        status_df = metrics.compute_status_distribution(eff_df)
        status_df["Status"] = status_df["Status"].replace(_STATUS_LABEL_MAP)
        status_df = status_df.groupby("Status", as_index=False)["Count"].sum()
        _dist_total = status_df["Count"].sum()
        status_df["Percentage"] = (status_df["Count"] / _dist_total * 100).round(2) if _dist_total > 0 else 0.0
        status_df["label"] = status_df.apply(
            lambda r: f"{int(r['Count'])} ({r['Percentage']:.2f}%)", axis=1
        )
        bar_fig = px.bar(
            status_df, x="Count", y="Status", orientation="h",
            color="Status", color_discrete_map=STATUS_COLORS,
            text="label",
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
        pie_fig.update_traces(texttemplate="%{label}<br>%{value} (%{percent:.2%})")
        pie_fig = make_chart_fig(pie_fig, "Completion Proportion")
        st.plotly_chart(pie_fig, use_container_width=True)

    st.markdown('<hr class="pm-divider">', unsafe_allow_html=True)

    # ── BOTTOM: Tables ──────────────────────────────────────────────
    render_section_header("Detailed Breakdown")
    col_left, col_right = st.columns(2)

    with col_left:
        st.caption("Department Progress")
        dept_df = metrics.compute_department_progress(eff_df)
        styled_dept = style_completion_table(dept_df, rules=[
            {"col": "Completion%", "op": "lt", "threshold": LOW_COMPLETION_THRESHOLD, "color": "#FEF2F2"},
        ]).format({"Completion%": "{:.2f}%"})
        st.dataframe(styled_dept, use_container_width=True, hide_index=True)

    with col_right:
        st.caption("Approver Workload")
        approver_df = metrics.compute_approver_workload(eff_df)
        avg_pending = float(approver_df["Pending"].mean()) if len(approver_df) > 0 else 0
        styled_approver = style_completion_table(approver_df, rules=[
            {"col": "Pending",     "op": "gt", "threshold": avg_pending,            "color": "#FFFBEB"},
            {"col": "Completion%", "op": "lt", "threshold": LOW_COMPLETION_THRESHOLD, "color": "#FEF2F2"},
        ]).format({"Completion%": "{:.2f}%"})
        st.dataframe(styled_approver, use_container_width=True, hide_index=True)

    st.markdown('<hr class="pm-divider">', unsafe_allow_html=True)

    render_section_header("Dept Group Comparison")
    dg_comp_df = metrics.compute_dept_group_comparison(eff_df, _dept_name_to_group)

    col_dg_bar, col_dg_stack = st.columns(2)

    with col_dg_bar:
        dg_sorted = dg_comp_df.sort_values("Completion%", ascending=True)
        _dg_chart_h = max(320, 48 * len(dg_sorted))
        dg_bar = px.bar(
            dg_sorted,
            x="Completion%", y="Department Group", orientation="h",
            color_discrete_sequence=["#8B5CF6"],
            text=dg_sorted.apply(
                lambda r: f"{int(r['Completed'])} / {int(r['Total'])} ({r['Completion%']:.2f}%)", axis=1
            ),
        )
        dg_bar = make_chart_fig(dg_bar, "Completion % by Dept Group")
        dg_bar.update_layout(showlegend=False, yaxis_title="", xaxis_title="Completion %", height=_dg_chart_h)
        st.plotly_chart(dg_bar, use_container_width=True)

    with col_dg_stack:
        dg_base = dg_comp_df.sort_values("Completion%", ascending=True)
        dg_stacked = dg_base.melt(
            id_vars=["Department Group", "Total"],
            value_vars=["Completed", "In Progress", "Not Started"],
            var_name="Status", value_name="Count",
        )
        dg_stacked["label"] = dg_stacked.apply(
            lambda r: f"{int(r['Count'])} ({r['Count'] / r['Total'] * 100:.2f}%)" if r["Count"] > 0 else "",
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
        dg_stacked_fig.update_layout(yaxis_title="", xaxis_title="Count", height=_dg_chart_h)
        st.plotly_chart(dg_stacked_fig, use_container_width=True)

    st.markdown('<hr class="pm-divider">', unsafe_allow_html=True)

    render_section_header("Department Detail Comparison")
    dept_comp_df = metrics.compute_department_comparison(eff_df)

    col_comp_bar, col_comp_stack = st.columns(2)

    with col_comp_bar:
        comp_sorted = dept_comp_df.sort_values("Completion%", ascending=True)
        _dept_chart_h = max(420, 36 * len(comp_sorted))
        bar_comp = px.bar(
            comp_sorted,
            x="Completion%", y="Department", orientation="h",
            color_discrete_sequence=["#3B82F6"],
            text=comp_sorted.apply(
                lambda r: f"{int(r['Completed'])} / {int(r['Total'])} ({r['Completion%']:.2f}%)", axis=1
            ),
        )
        bar_comp = make_chart_fig(bar_comp, "Completion % by Department")
        bar_comp.update_layout(showlegend=False, yaxis_title="", xaxis_title="Completion %", height=_dept_chart_h)
        st.plotly_chart(bar_comp, use_container_width=True)

    with col_comp_stack:
        comp_base = dept_comp_df.sort_values("Completion%", ascending=True)
        stacked_df = comp_base.melt(
            id_vars=["Department", "Total"],
            value_vars=["Completed", "In Progress", "Not Started"],
            var_name="Status", value_name="Count",
        )
        stacked_df["label"] = stacked_df.apply(
            lambda r: f"{int(r['Count'])} ({r['Count'] / r['Total'] * 100:.2f}%)" if r["Count"] > 0 else "",
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
        stacked_fig.update_layout(yaxis_title="", xaxis_title="Count", height=_dept_chart_h)
        st.plotly_chart(stacked_fig, use_container_width=True)

    st.markdown('<hr class="pm-divider">', unsafe_allow_html=True)

    render_section_header("Follow-up Required List")
    followup_df = metrics.get_followup_list(eff_df).copy()
    followup_df["Trạng thái"] = followup_df["Trạng thái"].replace(_STATUS_LABEL_MAP)
    followup_df = followup_df.rename(columns={
        "Nhân viên":  "Employee",
        "Phòng ban":  "Department",
        "Trạng thái": "Status",
        "Người duyệt": "Approver",
    })
    count = len(followup_df)
    if count > 0:
        eff_total = kpis["total"]
        followup_pct = round(count / eff_total * 100, 2) if eff_total > 0 else 0.0
        st.markdown(
            f'<span style="background:#FEF2F2;color:#DC2626;padding:.2rem .65rem;'
            f'border-radius:999px;font-size:.8rem;font-weight:700;">'
            f'⚠ {count} require follow-up ({followup_pct:.2f}% of effective total)</span>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<span style="background:#F0FDF4;color:#16A34A;padding:.2rem .65rem;'
            'border-radius:999px;font-size:.8rem;font-weight:700;">✓ No follow-up needed</span>',
            unsafe_allow_html=True,
        )
    st.dataframe(followup_df, use_container_width=True, hide_index=True)
