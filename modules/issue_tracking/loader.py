import io
import os
from typing import Optional
import pandas as pd
from config import ISSUE_SNAPSHOTS_DIR, ISSUE_SNAPSHOTS_CLOUD_PREFIX, SNAPSHOT_WINDOW
from utils import storage


def list_snapshot_files() -> list:
    """Sorted list of snapshot base filenames (oldest first)."""
    return storage.list_files(ISSUE_SNAPSHOTS_CLOUD_PREFIX, ISSUE_SNAPSHOTS_DIR)


def load_snapshot(filename: str) -> Optional[pd.DataFrame]:
    cloud_path = f"{ISSUE_SNAPSHOTS_CLOUD_PREFIX}{filename}"   # root-level in bucket
    local_path = os.path.join(ISSUE_SNAPSHOTS_DIR, filename)
    data = storage.load_binary(cloud_path, local_path)
    if data is None:
        return None
    try:
        return pd.read_excel(io.BytesIO(data), sheet_name="Summary", engine="openpyxl")
    except Exception:
        return None


def load_snapshots() -> list:
    """Return list of Summary DataFrames for the latest SNAPSHOT_WINDOW files (oldest first)."""
    files = list_snapshot_files()
    recent = files[-SNAPSHOT_WINDOW:]
    result = []
    for f in recent:
        df = load_snapshot(f)
        if df is not None:
            result.append(df)
    return result


def load_latest_snapshot() -> Optional[pd.DataFrame]:
    files = list_snapshot_files()
    if not files:
        return None
    return load_snapshot(files[-1])
