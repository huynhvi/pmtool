import pandas as pd


def _get(df, group, name):
    row = df[(df["Metric_Group"] == group) & (df["Metric_Name"] == name)]
    if row.empty:
        return 0, 0.0
    return int(row.iloc[0]["Metric_Count"]), float(row.iloc[0]["Metric_Percentage"])


def compute_kpis(df: pd.DataFrame) -> dict:
    total, _      = _get(df, "Total_Issues", "Total Issues")
    open_cnt, _   = _get(df, "Status", "Open")
    reopen_cnt, _ = _get(df, "Status", "Reopen")
    closed_cnt, _ = _get(df, "Status", "Closed")
    toconf_cnt, _ = _get(df, "Status", "To Confirm")
    return {
        "total":      total,
        "open":       open_cnt,
        "reopen":     reopen_cnt,
        "closed":     closed_cnt,
        "to_confirm": toconf_cnt,
    }


def compute_status_dist(df: pd.DataFrame) -> pd.DataFrame:
    rows = df[df["Metric_Group"] == "Status"][
        ["Metric_Name", "Metric_Count", "Metric_Percentage"]
    ].copy()
    rows.columns = ["Status", "Count", "Percentage"]
    return rows.reset_index(drop=True)


def compute_severity_dist(df: pd.DataFrame, group: str) -> pd.DataFrame:
    """group = 'Open_Severity' or 'Reopen_Severity'"""
    rows = df[df["Metric_Group"] == group][
        ["Metric_Name", "Metric_Count", "Metric_Percentage"]
    ].copy()
    rows.columns = ["Severity", "Count", "Percentage"]
    return rows.reset_index(drop=True)


def compute_type_dist(df: pd.DataFrame) -> pd.DataFrame:
    rows = df[df["Metric_Group"] == "Open_Reopen_Type"][
        ["Metric_Name", "Metric_Count", "Metric_Percentage"]
    ].copy()
    rows.columns = ["Type", "Count", "Percentage"]
    return rows.sort_values("Count", ascending=False).reset_index(drop=True)


def compute_trend(snapshots: list) -> tuple:
    """
    snapshots: list of Summary DataFrames, oldest first.
    Returns (trend_df, pct_changes_dict).
    """
    rows = []
    for snap_df in snapshots:
        snap_id   = snap_df["Snapshot_ID"].iloc[0]   if "Snapshot_ID"   in snap_df.columns else "—"
        snap_date = str(snap_df["Snapshot_Date"].iloc[0])[:19] if "Snapshot_Date" in snap_df.columns else "—"
        total, _      = _get(snap_df, "Total_Issues", "Total Issues")
        open_cnt, _   = _get(snap_df, "Status", "Open")
        reopen_cnt, _ = _get(snap_df, "Status", "Reopen")
        closed_cnt, _ = _get(snap_df, "Status", "Closed")
        toconf_cnt, _ = _get(snap_df, "Status", "To Confirm")
        rows.append({
            "Snapshot":   snap_id,
            "Date":       snap_date,
            "Total":      total,
            "Open":       open_cnt,
            "Reopen":     reopen_cnt,
            "Closed":     closed_cnt,
            "To Confirm": toconf_cnt,
        })

    trend_df = pd.DataFrame(rows)

    pct_changes = {}
    if len(rows) >= 2:
        cur, prev = rows[-1], rows[-2]

        def pct(c, p):
            return round((c - p) / p * 100, 2) if p != 0 else 0.0

        pct_changes = {
            "total":      pct(cur["Total"],      prev["Total"]),
            "open":       pct(cur["Open"],       prev["Open"]),
            "reopen":     pct(cur["Reopen"],     prev["Reopen"]),
            "closed":     pct(cur["Closed"],     prev["Closed"]),
            "to_confirm": pct(cur["To Confirm"], prev["To Confirm"]),
        }

    return trend_df, pct_changes


def compute_evaluation(pct_changes: dict) -> list:
    open_pct   = pct_changes.get("open",   0) or 0
    reopen_pct = pct_changes.get("reopen", 0) or 0
    closed_pct = pct_changes.get("closed", 0) or 0

    evaluations = []

    if open_pct > 0:
        evaluations.append({"level": "error",
            "message": f"Open issues increased by {abs(open_pct):.2f}% compared to the previous snapshot, indicating rising backlog risk."})
    elif open_pct < 0:
        evaluations.append({"level": "success",
            "message": f"Open issues decreased by {abs(open_pct):.2f}% compared to the previous snapshot, indicating issue backlog is improving."})

    if reopen_pct > 0:
        evaluations.append({"level": "error",
            "message": f"Reopen issues increased by {abs(reopen_pct):.2f}% compared to the previous snapshot, indicating quality risk is increasing."})
    elif reopen_pct < 0:
        evaluations.append({"level": "success",
            "message": f"Reopen issues decreased by {abs(reopen_pct):.2f}% compared to the previous snapshot, showing improvement in issue resolution quality."})

    if closed_pct > 0:
        evaluations.append({"level": "success",
            "message": f"Closed issues increased by {abs(closed_pct):.2f}% compared to the previous snapshot, showing progress in issue resolution."})
    elif closed_pct < 0:
        evaluations.append({"level": "warning",
            "message": f"Closed issues decreased by {abs(closed_pct):.2f}% compared to the previous snapshot — resolution rate may be slowing."})

    if not evaluations:
        evaluations.append({"level": "warning",
            "message": "No significant changes compared to the previous snapshot — system appears stable."})

    return evaluations
