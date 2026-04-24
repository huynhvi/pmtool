import streamlit as st
import pandas as pd

STATUS_COLORS = {
    "Open": "#DC2626", "Reopen": "#EA580C", "Closed": "#16A34A",
    "To Confirm": "#D97706",
    "High": "#DC2626", "Medium": "#D97706", "Low": "#16A34A",
    "Completed": "#16A34A", "In Progress": "#D97706", "Not Started": "#9CA3AF",
    "E_APPROVED": "#16A34A", "E_COMPLETED": "#16A34A", "E_WAITING_HANDLING": "#9CA3AF",
    "Approved": "#16A34A", "Awaiting Adjustment": "#D97706",
    "Awaiting Approval": "#D97706", "Awaiting Action": "#9CA3AF",
}

_CSS = """
<style>
.block-container { padding-top: 4rem !important; padding-bottom: 2rem !important; }
[data-testid="stMainBlockContainer"] { overflow: visible !important; }
[data-testid="stHtml"] { width: 100% !important; overflow: visible !important; }
#MainMenu { visibility: hidden; }
footer    { visibility: hidden; }

.pm-kpi-card {
    border-radius: 10px;
    padding: 1.1rem 1.25rem;
    border-left: 5px solid var(--card-accent);
    background: var(--card-bg);
    box-shadow: 0 1px 4px rgba(0,0,0,.07);
    height: 100%;
}
.pm-kpi-card .label {
    font-size: 0.75rem; color: #6B7280;
    text-transform: uppercase; letter-spacing: .06em; margin-bottom: .3rem;
}
.pm-kpi-card .value {
    font-size: 2rem; font-weight: 700; line-height: 1; color: #111827;
}
.pm-kpi-card .delta {
    font-size: 0.76rem; margin-top: .35rem; font-weight: 600;
}
.pm-kpi-green  { --card-accent: #16A34A; --card-bg: #F0FDF4; }
.pm-kpi-yellow { --card-accent: #D97706; --card-bg: #FFFBEB; }
.pm-kpi-red    { --card-accent: #DC2626; --card-bg: #FEF2F2; }
.pm-kpi-gray   { --card-accent: #6B7280; --card-bg: #F9FAFB; }

.pm-section-header {
    font-size: 0.78rem; font-weight: 700; letter-spacing: .08em;
    text-transform: uppercase; color: #6B7280;
    margin: 1.4rem 0 .65rem 0;
    padding-bottom: .35rem;
    border-bottom: 2px solid #E5E7EB;
}
.pm-divider {
    border: none; border-top: 1px solid #E5E7EB; margin: 1.1rem 0;
}
button[data-baseweb="tab"][aria-selected="true"] {
    border-bottom: 3px solid #2563EB !important;
    font-weight: 700 !important;
    color: #2563EB !important;
}
button[data-baseweb="tab"] { font-size: 0.9rem; }
.stDataFrame thead th { font-size: 0.78rem; background: #F3F4F6 !important; }
.stDataFrame tbody td { font-size: 0.82rem; }
</style>
"""


def inject_css():
    st.markdown(_CSS, unsafe_allow_html=True)


def render_kpi_cards(metrics: list):
    cols = st.columns(len(metrics))
    for col, m in zip(cols, metrics):
        color = m.get("color", "gray")
        delta_html = ""
        if m.get("delta") is not None:
            val = m["delta"]
            delta_color = "#16A34A" if str(val).lstrip("+-").replace(".", "").isdigit() and float(str(val).replace("%", "")) >= 0 else "#DC2626"
            arrow = "▲" if str(val).lstrip("-").replace("%", "").replace(".", "").isdigit() and not str(val).startswith("-") else "▼"
            delta_html = f'<div class="delta" style="color:{delta_color};">{arrow} {val}</div>'
        html = (
            f'<div class="pm-kpi-card pm-kpi-{color}">'
            f'<div class="label">{m["label"]}</div>'
            f'<div class="value">{m["value"]}</div>'
            f'{delta_html}'
            f'</div>'
        )
        col.markdown(html, unsafe_allow_html=True)


def render_section_header(title: str):
    st.markdown(f'<div class="pm-section-header">{title}</div>', unsafe_allow_html=True)


def make_chart_fig(fig, title: str):
    fig.update_layout(
        title_text=title,
        title_font_size=14,
        margin=dict(l=0, r=0, t=40, b=0),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font_family="sans-serif",
        legend=dict(orientation="h", yanchor="bottom", y=-0.25, xanchor="center", x=0.5),
    )
    return fig


def style_completion_table(df: pd.DataFrame, rules: list):
    """
    rules = [{"col": str, "op": "lt"|"gt", "threshold": float, "color": hex}]
    """
    def _styler(row):
        styles = [""] * len(row)
        for rule in rules:
            col = rule["col"]
            if col not in row.index:
                continue
            val = row[col]
            try:
                val = float(val)
            except (TypeError, ValueError):
                continue
            hit = (rule["op"] == "lt" and val < rule["threshold"]) or \
                  (rule["op"] == "gt" and val > rule["threshold"])
            if hit:
                col_idx = row.index.get_loc(col)
                styles[col_idx] = f"background-color: {rule['color']}"
        return styles

    return df.style.apply(_styler, axis=1)
