import pandas as pd
from config import SNAPSHOT_WINDOW


def compute_kpis(df: pd.DataFrame) -> dict:
    open_reopen = df[df["Status"].isin(["Open", "Reopen"])]
    result = {
        "total": len(df),
        "open": len(df[df["Status"] == "Open"]),
        "reopen": len(df[df["Status"] == "Reopen"]),
        "high_severity": len(open_reopen[open_reopen["Severity"] == "High"])
            if "Severity" in df.columns else 0,
    }
    if "Reopen Times" in df.columns:
        col = df["Reopen Times"]
        result["issues_reopened"] = int((col > 0).sum())
        result["avg_reopen_times"] = round(float(col.mean()), 2) if len(col) > 0 else 0.0
        result["max_reopen_times"] = int(col.max()) if len(col) > 0 else 0
    return result


def compute_status_distribution(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby("Status", as_index=False)
        .size()
        .rename(columns={"size": "Count"})
    )


def compute_severity_by_status(df: pd.DataFrame, status: str) -> pd.DataFrame:
    return (
        df[df["Status"] == status]
        .groupby("Severity", as_index=False)
        .size()
        .rename(columns={"size": "Count"})
    )


def compute_type_distribution(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df[df["Status"].isin(["Open", "Reopen"])]
        .groupby("Type", as_index=False)
        .size()
        .rename(columns={"size": "Count"})
        .sort_values("Count", ascending=False)
        .reset_index(drop=True)
    )


def compute_trend(df: pd.DataFrame) -> tuple:
    snapshots = sorted(df["Snapshot Date"].unique())[-SNAPSHOT_WINDOW:]
    rows = []
    for snap in snapshots:
        snap_df = df[df["Snapshot Date"] == snap]
        rows.append({
            "Snapshot Date": snap,
            "Total": len(snap_df),
            "Open": len(snap_df[snap_df["Status"] == "Open"]),
            "Reopen": len(snap_df[snap_df["Status"] == "Reopen"]),
        })
    trend_df = pd.DataFrame(rows).sort_values("Snapshot Date").reset_index(drop=True)

    pct_dict = {"total_pct": None, "open_pct": None, "reopen_pct": None}
    if len(trend_df) >= 2:
        cur, prev = trend_df.iloc[-1], trend_df.iloc[-2]

        def pct(c, p):
            return round((c - p) / p * 100, 1) if p != 0 else 0.0

        pct_dict = {
            "total_pct": pct(cur["Total"], prev["Total"]),
            "open_pct": pct(cur["Open"], prev["Open"]),
            "reopen_pct": pct(cur["Reopen"], prev["Reopen"]),
        }
    return trend_df, pct_dict


def compute_evaluation(pct_dict: dict, df: pd.DataFrame) -> list:
    evaluations = []
    open_pct = pct_dict.get("open_pct") or 0
    reopen_pct = pct_dict.get("reopen_pct") or 0

    open_reopen = df[df["Status"].isin(["Open", "Reopen"])]
    has_high = (
        "Severity" in df.columns and
        len(open_reopen[open_reopen["Severity"] == "High"]) > 0
    )

    if open_pct > 0 and reopen_pct > 0:
        evaluations.append({"level": "error",
            "message": f"Open issues increased by {abs(open_pct)}% and Reopen by {abs(reopen_pct)}% → risk is rising."})
    elif open_pct > 0:
        evaluations.append({"level": "error",
            "message": f"Open issues increased by {abs(open_pct)}% → risk is rising."})
    elif reopen_pct > 0:
        evaluations.append({"level": "error",
            "message": f"Reopen issues increased by {abs(reopen_pct)}% → risk is rising."})
    if has_high:
        evaluations.append({"level": "warning", "message": "Critical — High severity issues remain open."})
    if open_pct <= 0 and reopen_pct <= 0:
        parts = []
        if open_pct < 0:
            parts.append(f"Open issues decreased by {abs(open_pct)}%")
        if reopen_pct < 0:
            parts.append(f"Reopen issues decreased by {abs(reopen_pct)}%")
        msg = (" and ".join(parts) + " → quality is improving.") if parts else "Open/Reopen counts unchanged — system is stable."
        evaluations.append({"level": "success", "message": msg})

    return evaluations
