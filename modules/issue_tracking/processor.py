import json
from config import ISSUE_TRACKING_DATA
from utils import storage
from . import loader


def process_and_save(uploaded_file) -> dict:
    try:
        df, mapping, extra = loader.load_issue_data(uploaded_file)
    except Exception as e:
        return {"success": False, "rows": 0, "message": f"Failed to process file: {e}", "mapping": {}}

    mapping_filename = "issue_tracking_processed_mapping.json"
    mapping_local = ISSUE_TRACKING_DATA.replace(".json", "_mapping.json")
    try:
        storage.save_file(
            df.to_json(orient="records", force_ascii=False, date_format="iso"),
            "issue_tracking_processed.json",
            ISSUE_TRACKING_DATA,
        )
        storage.save_file(
            json.dumps(mapping, ensure_ascii=False, indent=2),
            mapping_filename,
            mapping_local,
        )
    except Exception as e:
        return {"success": False, "rows": 0, "message": f"Failed to save data: {e}", "mapping": mapping}

    return {"success": True, "rows": len(df), "message": f"Processed {len(df)} records successfully.", "mapping": mapping}
