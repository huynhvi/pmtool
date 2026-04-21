import pandas as pd
from config import COMPLETED_STATUSES, NOT_STARTED_STATUS


def compute_kpis(df: pd.DataFrame) -> dict:
    total = len(df)
    not_started = len(df[df["Trạng thái"] == NOT_STARTED_STATUS])
    completed = len(df[df["Trạng thái"].isin(COMPLETED_STATUSES)])
    in_progress = total - completed - not_started
    completion_rate = completed / total if total > 0 else 0.0
    return {
        "total": total,
        "completed": completed,
        "not_started": not_started,
        "in_progress": in_progress,
        "completion_rate": completion_rate,
    }


def compute_status_distribution(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby("Trạng thái", as_index=False)
        .size()
        .rename(columns={"Trạng thái": "Status", "size": "Count"})
    )


def compute_department_progress(df: pd.DataFrame) -> pd.DataFrame:
    total = df.groupby("Phòng ban").size().rename("Total")
    completed = (
        df[df["Trạng thái"].isin(COMPLETED_STATUSES)]
        .groupby("Phòng ban")
        .size()
        .rename("Completed")
    )
    result = pd.concat([total, completed], axis=1).fillna(0).reset_index()
    result.columns = ["Department", "Total", "Approved"]
    result["Approved"] = result["Approved"].astype(int)
    result["Completion%"] = (result["Approved"] / result["Total"] * 100).round(2)
    return result.sort_values("Completion%", ascending=False).reset_index(drop=True)


def compute_approver_workload(df: pd.DataFrame) -> pd.DataFrame:
    total = df.groupby("Người duyệt").size().rename("Total")
    completed = (
        df[df["Trạng thái"].isin(COMPLETED_STATUSES)]
        .groupby("Người duyệt")
        .size()
        .rename("Completed")
    )
    result = pd.concat([total, completed], axis=1).fillna(0).reset_index()
    result.columns = ["Approver", "Total", "Approved"]
    result["Approved"] = result["Approved"].astype(int)
    result["Pending"] = result["Total"] - result["Approved"]
    result["Completion%"] = (result["Approved"] / result["Total"] * 100).round(2)
    return result[["Approver", "Total", "Pending", "Completion%"]].sort_values("Completion%", ascending=False).reset_index(drop=True)


def get_followup_list(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df[df["Trạng thái"] == NOT_STARTED_STATUS][["Nhân viên", "Phòng ban", "Người duyệt"]]
        .reset_index(drop=True)
    )


def apply_filters(df: pd.DataFrame, dept: list, approver: list, status: list = None) -> pd.DataFrame:
    if dept:
        df = df[df["Phòng ban"].isin(dept)]
    if approver:
        df = df[df["Người duyệt"].isin(approver)]
    if status:
        df = df[df["Trạng thái"].isin(status)]
    return df
