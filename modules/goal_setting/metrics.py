import pandas as pd
from config import COMPLETED_STATUSES, NOT_STARTED_STATUS

_EXCLUDED_KEYWORDS = ["intern", "collaborator"]


def _is_excluded_position(pos) -> bool:
    if pd.isna(pos):
        return False
    pos_lower = str(pos).lower()
    return any(kw in pos_lower for kw in _EXCLUDED_KEYWORDS)


def get_effective_df(df: pd.DataFrame) -> pd.DataFrame:
    """Return df with Intern & Collaborator positions removed."""
    if "Vị trí" not in df.columns:
        return df
    return df[~df["Vị trí"].apply(_is_excluded_position)].copy()


def compute_kpis(df: pd.DataFrame) -> dict:
    total = len(df)
    not_started = len(df[df["Trạng thái"] == NOT_STARTED_STATUS])
    completed = len(df[df["Trạng thái"].isin(COMPLETED_STATUSES)])
    in_progress = total - completed - not_started
    completion_rate = completed / total if total > 0 else 0.0
    _pct = lambda n: round(n / total * 100, 2) if total > 0 else 0.0
    return {
        "total": total,
        "completed": completed,
        "not_started": not_started,
        "in_progress": in_progress,
        "completion_rate": completion_rate,
        "completed_pct":   _pct(completed),
        "in_progress_pct": _pct(in_progress),
        "not_started_pct": _pct(not_started),
    }


def compute_status_distribution(df: pd.DataFrame) -> pd.DataFrame:
    total = len(df)
    result = (
        df.groupby("Trạng thái", as_index=False)
        .size()
        .rename(columns={"Trạng thái": "Status", "size": "Count"})
    )
    result["Percentage"] = (result["Count"] / total * 100).round(2) if total > 0 else 0.0
    return result


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


def compute_department_comparison(df: pd.DataFrame) -> pd.DataFrame:
    total = df.groupby("Phòng ban").size().rename("Total")
    completed = (
        df[df["Trạng thái"].isin(COMPLETED_STATUSES)]
        .groupby("Phòng ban").size().rename("Completed")
    )
    not_started = (
        df[df["Trạng thái"] == NOT_STARTED_STATUS]
        .groupby("Phòng ban").size().rename("Not Started")
    )
    result = pd.concat([total, completed, not_started], axis=1).fillna(0).reset_index()
    result.columns = ["Department", "Total", "Completed", "Not Started"]
    result["Completed"] = result["Completed"].astype(int)
    result["Not Started"] = result["Not Started"].astype(int)
    result["In Progress"] = result["Total"] - result["Completed"] - result["Not Started"]
    result["Completion%"] = (result["Completed"] / result["Total"] * 100).round(2)
    return result.sort_values("Completion%", ascending=False).reset_index(drop=True)


def compute_dept_group_comparison(df: pd.DataFrame, dept_name_to_group: dict) -> pd.DataFrame:
    COLS = ["Department Group", "Total", "Completed", "Not Started", "In Progress", "Completion%"]
    if not dept_name_to_group:
        return pd.DataFrame(columns=COLS)
    tmp = df.copy()
    tmp["Dept_Group"] = tmp["Phòng ban"].map(dept_name_to_group)
    tmp = tmp.dropna(subset=["Dept_Group"])
    if tmp.empty:
        return pd.DataFrame(columns=COLS)
    total = tmp.groupby("Dept_Group").size().rename("Total")
    completed = (
        tmp[tmp["Trạng thái"].isin(COMPLETED_STATUSES)]
        .groupby("Dept_Group").size().rename("Completed")
    )
    not_started = (
        tmp[tmp["Trạng thái"] == NOT_STARTED_STATUS]
        .groupby("Dept_Group").size().rename("Not Started")
    )
    result = pd.concat([total, completed, not_started], axis=1).fillna(0).reset_index()
    result.columns = ["Department Group", "Total", "Completed", "Not Started"]
    result["Completed"] = result["Completed"].astype(int)
    result["Not Started"] = result["Not Started"].astype(int)
    result["In Progress"] = result["Total"] - result["Completed"] - result["Not Started"]
    result["Completion%"] = (result["Completed"] / result["Total"] * 100).round(2)
    return result.sort_values("Completion%", ascending=False).reset_index(drop=True)


def get_followup_list(df: pd.DataFrame) -> pd.DataFrame:
    cols = [c for c in ["Nhân viên", "Phòng ban", "Trạng thái", "Người duyệt"] if c in df.columns]
    return (
        df[~df["Trạng thái"].isin(COMPLETED_STATUSES)][cols]
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
