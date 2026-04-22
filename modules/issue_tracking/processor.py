import io
import os
import datetime
import pandas as pd
from config import ISSUE_SNAPSHOTS_DIR, ISSUE_SNAPSHOTS_CLOUD_PREFIX
from utils import storage

_STATUS_NORM = {
    "Open": "Open", "Re-Open": "Reopen", "Reopen": "Reopen",
    "Closed": "Closed", "Close": "Closed",
    "To Confirm": "To Confirm", "Toconfirm": "To Confirm",
}
_SEVERITY_NORM = {
    "High": "High",
    "Medium": "Medium", "Med": "Medium",
    "Low": "Low",
}
_TYPE_NORM = {
    "Bug": "Bug",
    "Configuration": "Configuration", "Config": "Configuration",
    "Improvement": "Improvement", "Improve": "Improvement",
}

_STATUS_CANDIDATES   = ["Status", "status", "STATUS", "Trạng thái", "Issue Status"]
_SEVERITY_CANDIDATES = ["Severity", "severity", "SEVERITY", "Mức độ", "Priority"]
_TYPE_CANDIDATES     = ["Type", "type", "TYPE", "Issue Type", "IssueType", "Category"]

_HEADER_KEYWORDS = {"status", "severity", "type", "issue", "id", "priority", "date", "trạng", "loại", "no.", "no"}


def _detect_header_row(raw_df) -> int:
    """Scan first 20 rows and return the index of the most likely header row."""
    best_row, best_score = 0, 0
    for idx in range(min(20, len(raw_df))):
        vals = [str(v).lower().strip() for v in raw_df.iloc[idx] if pd.notna(v) and str(v).strip() not in ("", "nan")]
        score = sum(1 for v in vals if any(kw in v for kw in _HEADER_KEYWORDS))
        if score > best_score:
            best_score, best_row = score, idx
    return best_row


def _find_col(df, candidates):
    lower_map = {c.lower(): c for c in df.columns}
    for name in candidates:
        if name.lower() in lower_map:
            return lower_map[name.lower()]
    return None


def _normalize(series, norm_map):
    def _norm(v):
        v = str(v).strip().title()
        return norm_map.get(v, v)
    return series.apply(_norm)


def process_and_save(uploaded_file) -> dict:
    source_file_name = getattr(uploaded_file, "name", "unknown")
    try:
        raw_df = pd.read_excel(uploaded_file, header=None, sheet_name="IssuesLog", engine="openpyxl")
        header_row = _detect_header_row(raw_df)
        uploaded_file.seek(0)
        df = pd.read_excel(uploaded_file, header=header_row, sheet_name="IssuesLog", engine="openpyxl")
    except Exception as e:
        return {"success": False, "message": f"Cannot read IssuesLog sheet: {e}"}

    df = df.dropna(how="all").reset_index(drop=True)
    # Strip whitespace from column names
    df.columns = [str(c).strip() for c in df.columns]
    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].astype(str).str.strip()

    status_col   = _find_col(df, _STATUS_CANDIDATES)
    severity_col = _find_col(df, _SEVERITY_CANDIDATES)
    type_col     = _find_col(df, _TYPE_CANDIDATES)

    if status_col is None:
        found = list(df.columns)
        return {"success": False, "message": f"Cannot find Status column in IssuesLog sheet. Columns found: {found}"}

    df[status_col] = _normalize(df[status_col], _STATUS_NORM)
    if severity_col:
        df[severity_col] = _normalize(df[severity_col], _SEVERITY_NORM)
    if type_col:
        df[type_col] = _normalize(df[type_col], _TYPE_NORM)

    now = datetime.datetime.now()
    snapshot_id   = now.strftime("Rawdata_%Y%m%d_%H%M%S")
    snapshot_date = now.strftime("%Y-%m-%d %H:%M:%S")
    total = len(df)

    rows = []

    def add_row(group, subgroup, name, count):
        pct = round(count / total * 100, 2) if total > 0 else 0.0
        rows.append({
            "Snapshot_ID":       snapshot_id,
            "Snapshot_Date":     snapshot_date,
            "Metric_Group":      group,
            "Metric_Subgroup":   subgroup,
            "Metric_Name":       name,
            "Metric_Count":      count,
            "Metric_Percentage": pct,
            "Base_Total_Issues": total,
        })

    add_row("Total_Issues",    "",         "Total Issues", total)

    for status in ["Open", "Reopen", "Closed", "To Confirm"]:
        add_row("Status", "Status", status, int((df[status_col] == status).sum()))

    if severity_col:
        open_df   = df[df[status_col] == "Open"]
        reopen_df = df[df[status_col] == "Reopen"]
        for sev in ["High", "Medium", "Low"]:
            add_row("Open_Severity",   "Severity", sev, int((open_df[severity_col]   == sev).sum()))
            add_row("Reopen_Severity", "Severity", sev, int((reopen_df[severity_col] == sev).sum()))

    if type_col:
        or_df = df[df[status_col].isin(["Open", "Reopen"])]
        for t in ["Bug", "Configuration", "Improvement"]:
            add_row("Open_Reopen_Type", "Type", t, int((or_df[type_col] == t).sum()))

    summary_df = pd.DataFrame(rows)

    # Schema validation
    required_cols = {
        "Snapshot_ID", "Snapshot_Date", "Metric_Group", "Metric_Subgroup",
        "Metric_Name", "Metric_Count", "Metric_Percentage", "Base_Total_Issues",
    }
    missing = required_cols - set(summary_df.columns)
    if missing:
        return {"success": False, "message": f"Schema validation failed — missing columns: {missing}"}
    if summary_df["Base_Total_Issues"].nunique() != 1:
        return {"success": False, "message": "Schema validation failed — Base_Total_Issues is inconsistent."}
    if summary_df["Metric_Count"].lt(0).any():
        return {"success": False, "message": "Schema validation failed — negative Metric_Count values."}

    # Build Excel
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        summary_df.to_excel(writer, sheet_name="Summary", index=False)
        pd.DataFrame([{
            "Snapshot_ID":       snapshot_id,
            "Snapshot_Date":     snapshot_date,
            "Source_File_Name":  source_file_name,
            "Source_Sheet_Name": "IssuesLog",
            "Total_Source_Rows": total,
            "Processed_By":      "system",
            "Processing_Status": "Success",
            "Error_Message":     "",
        }]).to_excel(writer, sheet_name="Metadata", index=False)

    excel_bytes = output.getvalue()

    filename   = f"{snapshot_id}.xlsx"
    local_path = os.path.join(ISSUE_SNAPSHOTS_DIR, filename)
    cloud_path = f"{ISSUE_SNAPSHOTS_CLOUD_PREFIX}{filename}"   # root-level in bucket
    try:
        storage.save_binary(excel_bytes, cloud_path, local_path)
    except Exception as e:
        return {"success": False, "message": f"Snapshot generated but failed to save: {e}"}

    return {
        "success":     True,
        "message":     f"Snapshot {snapshot_id} generated with {total} issues.",
        "snapshot_id": snapshot_id,
    }
