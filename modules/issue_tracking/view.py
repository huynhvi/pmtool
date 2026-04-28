import streamlit as st
import plotly.express as px
import pandas as pd
from . import loader, metrics
from utils.ui_helpers import render_kpi_cards, render_section_header, make_chart_fig, STATUS_COLORS

_EVAL_STYLE = {
    "error":   ("🔴", "#FEF2F2", "#DC2626"),
    "warning": ("🟡", "#FFFBEB", "#D97706"),
    "success": ("🟢", "#F0FDF4", "#16A34A"),
}


def _eval_badge(item: dict):
    icon, bg, border = _EVAL_STYLE[item["level"]]
    st.markdown(
        f'<div style="background:{bg};border-left:4px solid {border};'
        f'padding:.6rem 1rem;border-radius:6px;margin:.35rem 0;font-size:.88rem;">'
        f'{icon} {item["message"]}</div>',
        unsafe_allow_html=True,
    )


def render():
    snapshots = loader.load_snapshots()
    if not snapshots:
        st.info("No data available yet. Ask your Admin to upload and process the Issue Tracking file.")
        return

    latest    = snapshots[-1]
    snap_id   = latest["Snapshot_ID"].iloc[0]   if "Snapshot_ID"   in latest.columns else "—"
    snap_date = str(latest["Snapshot_Date"].iloc[0])[:19] if "Snapshot_Date" in latest.columns else "—"
    st.caption(f"Data source: **{snap_id}** | Generated: {snap_date} | {len(snapshots)} snapshot(s) loaded")

    kpis = metrics.compute_kpis(latest)

    # ── KPI ─────────────────────────────────────────────────────────
    render_section_header("Summary")
    render_kpi_cards([
        {"label": "Total Issues", "value": kpis["total"],      "color": "gray"},
        {"label": "Open",         "value": kpis["open"],       "color": "red"},
        {"label": "Reopen",       "value": kpis["reopen"],     "color": "yellow"},
        {"label": "Closed",       "value": kpis["closed"],     "color": "green"},
        {"label": "To Confirm",   "value": kpis["to_confirm"], "color": "yellow"},
        {"label": "Passed",       "value": kpis["passed"],     "color": "blue"},
    ])

    st.markdown('<hr class="pm-divider">', unsafe_allow_html=True)

    # ── Status + Severity Distribution ──────────────────────────────
    render_section_header("Distribution")

    status_df    = metrics.compute_status_dist(latest)
    has_severity = not latest[latest["Metric_Group"] == "Open_Severity"].empty
    has_type     = not latest[latest["Metric_Group"] == "Open_Reopen_Type"].empty

    if has_severity:
        col1, col2 = st.columns([0.9, 1.1])
        with col1:
            pie_fig = px.pie(
                status_df, names="Status", values="Count", hole=0.45,
                color="Status", color_discrete_map=STATUS_COLORS,
            )
            st.plotly_chart(make_chart_fig(pie_fig, "Issue Status Proportion"), use_container_width=True)
        with col2:
            sev_open   = metrics.compute_severity_dist(latest, "Open_Severity")
            sev_open["Status"] = "Open"
            sev_reopen = metrics.compute_severity_dist(latest, "Reopen_Severity")
            sev_reopen["Status"] = "Reopen"
            sev_combined = pd.concat([sev_open, sev_reopen], ignore_index=True)
            sev_fig = px.bar(
                sev_combined, x="Severity", y="Count", color="Status",
                barmode="group", color_discrete_map=STATUS_COLORS, text="Count",
            )
            st.plotly_chart(make_chart_fig(sev_fig, "Severity — Open vs Reopen"), use_container_width=True)
    else:
        pie_fig = px.pie(
            status_df, names="Status", values="Count", hole=0.45,
            color="Status", color_discrete_map=STATUS_COLORS,
        )
        st.plotly_chart(make_chart_fig(pie_fig, "Issue Status Proportion"), use_container_width=True)
        st.info("Severity column not detected in source file — severity breakdown is unavailable.")

    # ── Issue Type ──────────────────────────────────────────────────
    if has_type:
        st.markdown('<hr class="pm-divider">', unsafe_allow_html=True)
        render_section_header("Issue Type Breakdown (Open + Reopen)")
        type_df = metrics.compute_type_dist(latest)
        type_fig = px.bar(
            type_df, x="Type", y="Count", color="Type", text="Count",
            color_discrete_sequence=["#3B82F6", "#8B5CF6", "#10B981"],
        )
        st.plotly_chart(make_chart_fig(type_fig, "Issue Type Distribution"), use_container_width=True)
        st.dataframe(
            type_df.style.format({"Percentage": "{:.2f}%"}),
            use_container_width=True,
            hide_index=True,
        )

    # ── History / Trend ─────────────────────────────────────────────
    st.markdown('<hr class="pm-divider">', unsafe_allow_html=True)
    render_section_header("History — Latest 5 Snapshots")

    if len(snapshots) < 2:
        st.info(f"Only {len(snapshots)} snapshot available. Upload more files to see trend comparison.")
        return

    trend_df, pct_changes = metrics.compute_trend(snapshots)

    trend_fig = px.line(
        trend_df, x="Date", y=["Total", "Open", "Reopen", "Closed", "To Confirm", "Passed"],
        markers=True,
    )
    st.plotly_chart(make_chart_fig(trend_fig, "Issue Count Trend"), use_container_width=True)

    st.dataframe(trend_df, use_container_width=True, hide_index=True)

    st.subheader("Change vs Previous Snapshot")
    cols = st.columns(6)
    labels = [
        ("Total",      "total"),
        ("Open",       "open"),
        ("Reopen",     "reopen"),
        ("Closed",     "closed"),
        ("To Confirm", "to_confirm"),
        ("Passed",     "passed"),
    ]
    for col, (label, key) in zip(cols, labels):
        pct = pct_changes.get(key, 0) or 0
        if pct == 0:
            color, arrow = "#6B7280", "—"
            display = "0.00%"
        elif pct > 0:
            color, arrow = "#DC2626", "▲"
            display = f"{abs(pct):.2f}%"
        else:
            color, arrow = "#16A34A", "▼"
            display = f"{abs(pct):.2f}%"
        col.markdown(
            f'<div style="background:#F9FAFB;border-radius:8px;padding:.75rem 1rem;">'
            f'<div style="font-size:.72rem;color:#6B7280;text-transform:uppercase;">{label}</div>'
            f'<div style="font-size:1.3rem;font-weight:700;color:{color};margin-top:.2rem;">'
            f'{arrow} {display}</div></div>',
            unsafe_allow_html=True,
        )

    st.markdown('<hr class="pm-divider">', unsafe_allow_html=True)
    render_section_header("Evaluation")
    for item in metrics.compute_evaluation(pct_changes):
        _eval_badge(item)
