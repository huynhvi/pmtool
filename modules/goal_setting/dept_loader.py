import pandas as pd
from functools import lru_cache
from config import DEPARTMENT_DATA


_SHEET_NAME = "Updated via PM Tool 28Ap26"
_PT_COL     = "PM Tool-Deaprtment List - 28Apr26"


@lru_cache(maxsize=1)
def load_department_df() -> pd.DataFrame:
    try:
        df = pd.read_excel(DEPARTMENT_DATA, sheet_name=_SHEET_NAME)
        df.columns = [c.strip() for c in df.columns]
        # Replace name with PM Tool label where it is non-null and non-blank —
        # goal data uses PM Tool names, not internal names.
        if _PT_COL in df.columns:
            mask = df[_PT_COL].notna() & (df[_PT_COL].astype(str).str.strip() != "") \
                   & (df[_PT_COL].astype(str).str.strip() != "nan")
            df.loc[mask, "name"] = df.loc[mask, _PT_COL].astype(str).str.strip()
            df = df.drop(columns=[_PT_COL])
        df.columns = [c.strip().lower() for c in df.columns]
        # Drop rows with blank/unnamed code or name
        df = df[df["code"].astype(str).str.strip().ne("") &
                df["name"].astype(str).str.strip().ne("nan") &
                df["name"].astype(str).str.strip().ne("")]
        return df.dropna(subset=["code", "name"]).reset_index(drop=True)
    except Exception:
        return pd.DataFrame(columns=["code", "name", "type", "parent_code", "manager"])


def build_children_by_name(dept_df: pd.DataFrame) -> dict:
    code_to_name = dict(zip(dept_df["code"], dept_df["name"]))
    children: dict = {row["name"]: [] for _, row in dept_df.iterrows()}
    for _, row in dept_df.iterrows():
        parent_code = row.get("parent_code")
        if pd.notna(parent_code):
            parent_name = code_to_name.get(parent_code)
            if parent_name in children:
                children[parent_name].append(row["name"])
    return children


def get_all_descendant_names(selected_names: list, children_by_name: dict) -> set:
    result: set = set()
    stack = list(selected_names)
    while stack:
        name = stack.pop()
        if name not in result:
            result.add(name)
            stack.extend(children_by_name.get(name, []))
    return result


def build_dept_name_to_group(dept_df: pd.DataFrame) -> dict:
    """Returns {dept_name: dept_group_name} by walking each dept up to its DEPT_GROUP ancestor."""
    if dept_df.empty:
        return {}
    code_to_name = dict(zip(dept_df["code"], dept_df["name"]))
    by_name = {row["name"]: row for _, row in dept_df.iterrows()}

    def find_group(start: str):
        name = start
        visited: set = set()
        while True:
            if name in visited:
                return None  # cycle guard
            visited.add(name)
            row = by_name.get(name)
            if row is None:
                return None
            if str(row["type"]).upper() == "DEPT_GROUP":
                return name
            parent_code = row["parent_code"]
            if pd.isna(parent_code):
                return None
            parent_name = code_to_name.get(parent_code)
            if parent_name is None:
                return None
            name = parent_name

    return {row["name"]: g for _, row in dept_df.iterrows()
            if (g := find_group(row["name"])) is not None}


def build_filter_options(dept_df: pd.DataFrame, goal_depts: list) -> tuple:
    """Returns (options, display_to_name, children_by_name).

    options: ordered display labels with hierarchy indentation
    display_to_name: maps each display label back to the actual dept name
    children_by_name: name -> [child names], used for descendant expansion
    """
    if dept_df.empty:
        flat = sorted(goal_depts)
        return flat, {d: d for d in flat}, {}

    children_by_name = build_children_by_name(dept_df)
    all_names = set(dept_df["name"])
    code_to_name = dict(zip(dept_df["code"], dept_df["name"]))

    roots = []
    for _, row in dept_df.iterrows():
        parent_code = row.get("parent_code")
        parent_name = code_to_name.get(parent_code) if pd.notna(parent_code) else None
        if parent_name is None or parent_name not in all_names:
            roots.append(row["name"])

    ordered: list = []
    visited: set = set()
    _NBSP = " "

    def traverse(name: str, depth: int):
        if name in visited:
            return
        visited.add(name)
        prefix = _NBSP * 4 * depth
        ordered.append((f"{prefix}{name}", name))
        for child in children_by_name.get(name, []):
            traverse(child, depth + 1)

    for root in roots:
        traverse(root, 0)

    # Append goal depts not found in the dept Excel (orphans)
    hierarchy_names = {item[1] for item in ordered}
    for d in sorted(goal_depts):
        if d not in hierarchy_names:
            ordered.append((d, d))

    options = [item[0] for item in ordered]
    display_to_name = {item[0]: item[1] for item in ordered}
    return options, display_to_name, children_by_name
