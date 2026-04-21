import json
import os
import anthropic

STANDARD_FIELDS = ["Issue ID", "Status", "Severity", "Type", "Reopen Times", "Snapshot Date"]

_FALLBACK = {
    "header_row": 0,
    "noise_rows": [],
    "mapping": {field: {"column": None, "confidence": "none"} for field in STANDARD_FIELDS},
    "normalizations": {"Status": {}, "Severity": {}},
}

_PROMPT = """\
You are analyzing a raw Excel file to prepare it for a dashboard.

Raw file content (first 20 rows, 0-indexed):
{raw_rows_json}

Task:
1. Find the header row (0-based index). Headers contain field names like "Issue ID", "Status", "Severity", "No.", "Date", etc. Rows above this are titles or notes.
2. Find noise rows to skip: title rows, note rows (e.g. "Below area is updated by..."), blank rows. Do NOT include the header row or valid data rows.
3. Map these standard fields to header column names: Issue ID, Status, Severity, Type, Reopen Times, Snapshot Date.
   - "Reopen Times" is the number of times an issue was reopened (look for: reopen count, no. reopen, reopen times, etc.)
   - Confidence: high = obvious match, medium = likely match, low = uncertain, none = not found.
4. Produce value normalizations for Status and Severity columns: scan data rows and list every distinct raw value, map it to the canonical form.
   - Canonical Status values: Open, Closed, Reopen, To Confirm
   - Canonical Severity values: High, Medium, Low

Respond ONLY with this exact JSON structure, no extra text, no markdown:
{{
  "header_row": <int>,
  "noise_rows": [<int>, ...],
  "mapping": {{
    "Issue ID":      {{"column": "<name or null>", "confidence": "<high|medium|low|none>"}},
    "Status":        {{"column": "<name or null>", "confidence": "<high|medium|low|none>"}},
    "Severity":      {{"column": "<name or null>", "confidence": "<high|medium|low|none>"}},
    "Type":          {{"column": "<name or null>", "confidence": "<high|medium|low|none>"}},
    "Reopen Times":  {{"column": "<name or null>", "confidence": "<high|medium|low|none>"}},
    "Snapshot Date": {{"column": "<name or null>", "confidence": "<high|medium|low|none>"}}
  }},
  "normalizations": {{
    "Status":   {{"<raw_value>": "<canonical>"}},
    "Severity": {{"<raw_value>": "<canonical>"}}
  }}
}}"""


def _get_api_key():
    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        try:
            import streamlit as st
            key = st.secrets.get("ANTHROPIC_API_KEY")
        except Exception:
            pass
    return key


def analyze_file(raw_rows: list) -> dict:
    api_key = _get_api_key()
    if not api_key:
        return _FALLBACK

    try:
        client = anthropic.Anthropic(api_key=api_key)
        raw_rows_json = json.dumps(raw_rows, ensure_ascii=False, default=str)
        message = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=1024,
            messages=[{"role": "user", "content": _PROMPT.format(raw_rows_json=raw_rows_json)}],
        )
        raw = message.content[0].text.strip()
        result = json.loads(raw)

        # Defensive defaults
        result.setdefault("header_row", 0)
        result.setdefault("noise_rows", [])
        result.setdefault("normalizations", {"Status": {}, "Severity": {}})
        result["normalizations"].setdefault("Status", {})
        result["normalizations"].setdefault("Severity", {})
        mapping = result.setdefault("mapping", {})
        for field in STANDARD_FIELDS:
            mapping.setdefault(field, {"column": None, "confidence": "none"})

        return result
    except Exception:
        return _FALLBACK


def map_columns(columns: list) -> dict:
    """Compatibility shim — returns only the mapping sub-dict."""
    return _FALLBACK["mapping"]
