import streamlit as st
import plotly.express as px
import pandas as pd
from . import loader, metrics
from utils.ui_helpers import (
    render_kpi_cards, render_section_header, make_chart_fig, STATUS_COLORS,
)

_EVAL_STYLE = {
    "error":   ("🔴", "#FEF2F2", "#DC2626"),
    "warning": ("🟡", "#FFFBEB", "#D97706"),
    "success": ("🟢", "#F0FDF4", "#16A34A"),
}


def _has(mapping: dict, field: str) -> bool:
    m = mapping.get(field, {})
    return m.get("column") is not None and m.get("confidence") != "none"


def _warn_if_low(mapping: dict, field: str):
    conf = mapping.get(field, {}).get("confidence", "none")
    if conf in ("low", "medium"):
        st.warning(f'"{field}" mapped with {conf} confidence — results may be inaccurate.')


def _eval_badge(item: dict):
    icon, bg, border = _EVAL_STYLE[item["level"]]
    st.markdown(
        f'<div style="background:{bg};border-left:4px solid {border};'
        f'padding:.6rem 1rem;border-radius:6px;margin:.35rem 0;font-size:.88rem;">'
        f'{icon} {item["message"]}</div>',
        unsafe_allow_html=True,
    )


def render():
    df, mapping = loader.load_processed_data()
    if df is None:
        st.info("No data available yet. Ask your Admin to upload and process the Issue Tracking file.")
        return

    if not _has(mapping, "Status"):
        st.error("Status column not found — cannot render dashboard. Check the column mapping above.")
        return

    kpis = metrics.compute_kpis(df)

    # ── TOP: KPI cards ──────────────────────────────────────────────
    render_section_header("Summary")
    kpi_list = [
        {"label": "Total Issues", "value": kpis["total"],  "color": "gray"},
        {"label": "Open",         "value": kpis["open"],   "color": "red"},
        {"label": "Reopen",       "value": kpis["reopen"], "color": "yellow"},
    ]
    if _has(mapping, "Severity"):
        kpi_list.append({"label": "High Severity", "value": kpis["high_severity"], "color": "red"})
    if _has(mapping, "Reopen Times"):
        kpi_list.append({"label": "Issues Reopened", "value": kpis.get("issues_reopened", 0), "color": "yellow"})
    render_kpi_cards(kpi_list)

    st.markdown('<hr class="pm-divider">', unsafe_allow_html=True)

    # ── MIDDLE: Charts ──────────────────────────────────────────────
    render_section_header("Distribution")

    has_severity = _has(mapping, "Severity")
    has_snapshot = _has(mapping, "Snapshot Date")

    if has_severity:
        col1, col2 = st.columns([0.9, 1.1])
        with col1:
            _warn_if_low(mapping, "Status")
            status_df = metrics.compute_status_distribution(df)
            pie_fig = px.pie(
                status_df, names="Status", values="Count", hole=0.45,
                color="Status", color_discrete_map=STATUS_COLORS,
            )
            pie_fig = make_chart_fig(pie_fig, "Issue Status Proportion")
            st.plotly_chart(pie_fig, use_container_width=True)
        with col2:
            _warn_if_low(mapping, "Severity")
            sev_open = metrics.compute_severity_by_status(df, "Open")
            sev_open["Status"] = "Open"
            sev_reopen = metrics.compute_severity_by_status(df, "Reopen")
            sev_reopen["Status"] = "Reopen"
            sev_combined = pd.concat([sev_open, sev_reopen], ignore_index=True)
            sev_fig = px.bar(
                sev_combined, x="Severity", y="Count", color="Status",
                barmode="group", color_discrete_map=STATUS_COLORS, text="Count",
            )
            sev_fig = make_chart_fig(sev_fig, "Severity — Open vs Reopen")
            st.plotly_chart(sev_fig, use_container_width=True)
    else:
        _warn_if_low(mapping, "Status")
        status_df = metrics.compute_status_distribution(df)
        pie_fig = px.pie(
            status_df, names="Status", values="Count", hole=0.45,
            color="Status", color_discrete_map=STATUS_COLORS,
        )
        pie_fig = make_chart_fig(pie_fig, "Issue Status Proportion")
        st.plotly_chart(pie_fig, use_container_width=True)
        st.info("Severity column not detected — severity breakdown is unavailable.")

    if has_snapshot:
        st.markdown('<hr class="pm-divider">', unsafe_allow_html=True)
        render_section_header("Trend — Last 5 Snapshots")
        _warn_if_low(mapping, "Snapshot Date")
        trend_df, pct_dict = metrics.compute_trend(df)

        if len(trend_df) >= 2:
            trend_fig = px.line(
                trend_df, x="Snapshot Date", y=["Total", "Open", "Reopen"],
                markers=True, color_discrete_map=STATUS_COLORS,
            )
            trend_fig = make_chart_fig(trend_fig, "")
            st.plotly_chart(trend_fig, use_container_width=True)

            c1, c2, c3 = st.columns(3)
            for col, label, key in [(c1, "Total Change", "total_pct"), (c2, "Open Change", "open_pct"), (c3, "Reopen Change", "reopen_pct")]:
                pct = pct_dict.get(key, 0) or 0
                color = "#DC2626" if pct > 0 else "#16A34A"
                arrow = "▲" if pct > 0 else "▼"
                col.markdown(
                    f'<div style="background:#F9FAFB;border-radius:8px;padding:.75rem 1rem;">'
                    f'<div style="font-size:.72rem;color:#6B7280;text-transform:uppercase;letter-spacing:.05em;">{label}</div>'
                    f'<div style="font-size:1.4rem;font-weight:700;color:{color};margin-top:.2rem;">{arrow} {abs(pct)}%</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
        else:
            st.info("Upload a file with at least 2 snapshot dates to see trend data.")
    else:
        st.info("Snapshot Date column not detected — trend section is unavailable.")

    st.markdown('<hr class="pm-divider">', unsafe_allow_html=True)

    # ── BOTTOM: Tables + Evaluation ─────────────────────────────────
    if _has(mapping, "Type"):
        render_section_header("Issue Type Breakdown (Open + Reopen)")
        _warn_if_low(mapping, "Type")
        type_df = metrics.compute_type_distribution(df)
        st.dataframe(type_df, use_container_width=True, hide_index=True)
        st.markdown('<hr class="pm-divider">', unsafe_allow_html=True)
    else:
        st.info("Type column not detected — issue type breakdown is unavailable.")

    if has_snapshot:
        render_section_header("Evaluation")
        trend_df, pct_dict = metrics.compute_trend(df)
        evaluations = metrics.compute_evaluation(pct_dict, df)
        for item in evaluations:
            _eval_badge(item)
