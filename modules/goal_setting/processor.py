import pandas as pd
from config import GOAL_SETTING_DATA
from utils import masking, storage

REQUIRED_COLUMNS = ["Nhân viên", "Phòng ban", "Vị trí", "Tên phiếu mục tiêu", "Trạng thái", "Người duyệt"]


def process_and_save(uploaded_file) -> dict:
    try:
        df = pd.read_excel(uploaded_file, engine="openpyxl")
    except Exception as e:
        return {"success": False, "rows": 0, "message": f"Failed to read file: {e}"}

    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        return {"success": False, "rows": 0, "message": f"Missing required columns: {', '.join(missing)}"}

    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].astype(str).str.strip()

    df["Nhân viên"] = masking.mask_name_series(df["Nhân viên"])
    df["Người duyệt"] = masking.mask_name_series(df["Người duyệt"])

    try:
        storage.save_file(
            df.to_json(orient="records", force_ascii=False),
            "goal_setting_processed.json",
            GOAL_SETTING_DATA,
        )
    except Exception as e:
        return {"success": False, "rows": 0, "message": f"Failed to save data: {e}"}

    return {"success": True, "rows": len(df), "message": f"Processed {len(df)} records successfully."}
