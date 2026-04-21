import io
import json
import pandas as pd
from config import ISSUE_TRACKING_DATA
from utils import storage
from . import column_mapper


def load_issue_data(uploaded_file) -> tuple:
    # Step 1 — read raw with no header assumption from IssuesLog sheet
    raw_df = pd.read_excel(uploaded_file, header=None, sheet_name="IssuesLog", engine="openpyxl")

    # Step 2 — extract sample rows for AI
    sample = raw_df.head(20).fillna("").astype(str).values.tolist()

    # Step 3 — AI analysis
    analysis = column_mapper.analyze_file(sample)
    header_row = int(analysis.get("header_row", 0))
    noise_rows = set(analysis.get("noise_rows", []))
    mapping = analysis["mapping"]
    normalizations = analysis.get("normalizations", {"Status": {}, "Severity": {}})

    # Step 4 — rewind and re-read with correct header
    uploaded_file.seek(0)
    df = pd.read_excel(uploaded_file, header=header_row, sheet_name="IssuesLog", engine="openpyxl")

    # Step 5 — drop noise rows (translate raw indices to df indices)
    df_noise = [r - header_row - 1 for r in noise_rows if r > header_row]
    df = df.drop(index=[i for i in df_noise if i in df.index], errors="ignore")

    # Step 6 — drop fully blank rows
    df = df.dropna(how="all").reset_index(drop=True)

    # Step 7 — strip whitespace
    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].astype(str).str.strip()

    # Step 8 — rename columns
    rename = {
        m["column"]: field
        for field, m in mapping.items()
        if m["column"] is not None and m["confidence"] != "none"
    }
    df.rename(columns=rename, inplace=True)

    # Step 9 — validate: if renamed column not actually in df, mark as none
    for field, m in mapping.items():
        if m["column"] is not None and field not in df.columns:
            m["confidence"] = "none"
            m["column"] = None

    # Step 10 — apply value normalizations per column
    for field in ("Status", "Severity"):
        norms = normalizations.get(field, {})
        if norms and field in df.columns:
            df[field] = df[field].replace(norms)

    # Step 11 — coerce Reopen Times
    if "Reopen Times" in df.columns:
        df["Reopen Times"] = pd.to_numeric(df["Reopen Times"], errors="coerce").fillna(0).astype(int)

    # Step 12 — parse Snapshot Date
    if "Snapshot Date" in df.columns:
        df["Snapshot Date"] = pd.to_datetime(df["Snapshot Date"], errors="coerce")
        df = df.dropna(subset=["Snapshot Date"])

    extra = {
        "header_row": header_row,
        "noise_rows": list(noise_rows),
        "normalizations": normalizations,
    }
    return df, mapping, extra


def load_processed_data() -> tuple:
    content = storage.load_file("issue_tracking_processed.json", ISSUE_TRACKING_DATA)
    if content is None:
        return None, {}
    df = pd.read_json(io.StringIO(content), orient="records")
    if "Snapshot Date" in df.columns:
        df["Snapshot Date"] = pd.to_datetime(df["Snapshot Date"], errors="coerce")

    mapping_local = ISSUE_TRACKING_DATA.replace(".json", "_mapping.json")
    mapping_content = storage.load_file("issue_tracking_processed_mapping.json", mapping_local)
    mapping = json.loads(mapping_content) if mapping_content else {}
    return df, mapping
