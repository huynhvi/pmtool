"""
Dual-mode file storage.
- Local dev: reads/writes files under DATA_DIR
- Streamlit Cloud: reads/writes to Supabase Storage bucket
Switches automatically based on whether st.secrets["supabase"] exists.
"""
import os
import io
import streamlit as st

BUCKET = "pmtool-data"


def _use_cloud() -> bool:
    try:
        return "supabase" in st.secrets
    except Exception:
        return False


@st.cache_resource
def _supabase():
    from supabase import create_client
    return create_client(
        st.secrets["supabase"]["url"],
        st.secrets["supabase"]["key"],
    )


def save_file(content: str, filename: str, local_path: str) -> None:
    """Save UTF-8 string. Overwrites if exists."""
    if _use_cloud():
        client = _supabase()
        data = content.encode("utf-8")
        try:
            client.storage.from_(BUCKET).remove([filename])
        except Exception:
            pass
        client.storage.from_(BUCKET).upload(
            filename, data, {"content-type": "application/json", "upsert": "true"}
        )
    else:
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        with open(local_path, "w", encoding="utf-8") as f:
            f.write(content)


def load_file(filename: str, local_path: str) -> str | None:
    """Load UTF-8 string. Returns None if file not found."""
    if _use_cloud():
        try:
            data = _supabase().storage.from_(BUCKET).download(filename)
            return data.decode("utf-8")
        except Exception:
            return None
    else:
        if not os.path.exists(local_path):
            return None
        with open(local_path, encoding="utf-8") as f:
            return f.read()


def file_info(filename: str, local_path: str) -> str:
    """Returns a human-readable status string for the Admin panel."""
    if _use_cloud():
        content = load_file(filename, local_path)
        if content is None:
            return "No data processed yet."
        try:
            import json
            rows = len(json.loads(content))
            return f"{rows} records available"
        except Exception:
            return "Data available"
    else:
        if not os.path.exists(local_path):
            return "No data processed yet."
        import datetime
        import json
        mtime = os.path.getmtime(local_path)
        ts = datetime.datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M")
        try:
            with open(local_path, encoding="utf-8") as f:
                rows = len(json.load(f))
            return f"Last processed: {ts} | {rows} records"
        except Exception:
            return f"Last processed: {ts}"
