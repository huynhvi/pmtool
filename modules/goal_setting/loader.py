import io
import pandas as pd
from config import GOAL_SETTING_DATA
from utils import masking, storage

REQUIRED_COLUMNS = ["Nhân viên", "Phòng ban", "Vị trí", "Tên phiếu mục tiêu", "Trạng thái", "Người duyệt"]


def load_goal_data() -> pd.DataFrame:
    content = storage.load_file("goal_setting_processed.json", GOAL_SETTING_DATA)
    if content is None:
        return None
    df = pd.read_json(io.StringIO(content), orient="records")
    if "Nhân viên" in df.columns:
        df["Nhân viên"] = masking.mask_name_series(df["Nhân viên"])
    if "Người duyệt" in df.columns:
        df["Người duyệt"] = masking.mask_name_series(df["Người duyệt"])
    return df
