# PMTool — Project Context & Enhancement History

> **This file is the centralized project memory for Claude Code.**
> Every new requirement or enhancement must be appended to the Enhancement History section below.
> Read this file first before re-reading individual source files.

---

## Project Overview

**PMTool** is a Streamlit-based Project Management Dashboard built for VNG Games.
It tracks two primary domains:
1. **Goal Setting** — employee goal-sheet completion status across departments
2. **Issue Tracking** — bug/issue lifecycle with severity, trend analysis, and snapshots

**Build version:** v2.2 (2026-04-29)
**Python:** 3.11.0
**Key deps:** streamlit==1.56.0, pandas>=2.0.0, plotly>=5.18.0, openpyxl>=3.1.0, supabase>=2.3.0

---

## Architecture

```
app.py                          # Streamlit entry point; auth gate; tab routing
auth.py                         # Login / logout; role-based session state
config.py                       # All global constants (statuses, paths, thresholds)
requirements.txt / runtime.txt  # Dependencies & Python version

modules/
  goal_setting/
    loader.py       # Load processed JSON; mask employee/approver names
    processor.py    # Raw Excel → JSON (validates required columns)
    metrics.py      # KPI computation, department progress, approver workload
    dept_loader.py  # Department hierarchy from Excel; build filter trees
    view.py         # Streamlit UI: KPI cards, charts, tables, follow-up list

  issue_tracking/
    loader.py       # Load snapshots (latest SNAPSHOT_WINDOW=5)
    processor.py    # Raw Excel → snapshot Excel with Summary sheet
    metrics.py      # KPIs, trends, severity, type breakdown, evaluations
    column_mapper.py# Standardise raw Excel column names
    view.py         # Dashboard: KPIs, status/severity charts, trends, badges

  admin/
    view.py         # Upload & process Goal Setting / Issue Tracking files

utils/
  storage.py        # Dual-mode: local filesystem OR Supabase cloud
  ui_helpers.py     # KPI cards, section headers, chart formatting, CSS, STATUS_COLORS
  masking.py        # Name abbreviation for privacy

Dashboard/Department/           # Department hierarchy Excel files
data/                           # Processed JSON & issue snapshots
```

---

## Key Constants (config.py)

```python
COMPLETED_STATUSES   = ["E_APPROVED", "E_CANCELLED", "Đã duyệt", "Hủy", "Approved", "Cancelled"]
IN_PROGRESS_STATUSES = ["E_WAITING_APPROVE", "E_ADJUST", "Chờ duyệt", "Yêu cầu điều chỉnh"]
NOT_STARTED_STATUSES = ["E_WAITING_HANDLING", "Chờ xử lý"]
SNAPSHOT_WINDOW      = 5
LOW_COMPLETION_THRESHOLD = 50.0   # % below which rows are highlighted red
```

**Department hierarchy file:**
`Dashboard/Department/vngg_department_updated 28Apr26.xlsx`

---

## Status Label Map (view.py — Goal Setting)

| Raw code | Display label |
|---|---|
| E_WAITING_HANDLING / Chờ xử lý | Not Started |
| E_WAITING_APPROVE / Chờ duyệt | Awaiting Approval |
| E_ADJUST / Yêu cầu điều chỉnh | Awaiting Adjustment |
| E_APPROVED / Đã duyệt / Approved | Approved |
| E_CANCELLED / Hủy / Cancelled | Cancelled |

---

## Exclusion Logic

Effective dataset = all rows MINUS:
1. Records where `Vị trí` contains "intern" or "collaborator" (case-insensitive partial match)
2. Records where `Phòng ban.strip().lower() == "senior management team"`

Both exclusions live in `metrics.get_effective_df()`. Applies to: KPI Summary, Status Distribution, Dept Group Comparison, Dept Detail Comparison, Approver Workload, Follow-up List, all % calculations.

## Department Code Display

HR structure: `Dashboard/Department/HR_structure.xlsx` → Sheet1, columns `Mã phòng ban` / `Tên phòng ban`
Loader: `dept_loader.load_hr_structure()` + `dept_loader.build_dept_name_to_code(hr_df)`
Mapping: `dept_name → dept_code` (display-only — all aggregation/hierarchy logic stays name-based)
Fallback: full name rendered if code not in mapping
Applied in: Department filter, Dept Group chart Y-axis, Dept Detail chart Y-axis, Department Progress table

---

## Role-Based Access

| Role | Tabs visible |
|---|---|
| admin | Admin + Goal Setting + Issue Tracking |
| user | Goal Setting + Issue Tracking |

Accounts are loaded from Streamlit secrets; fallback hardcoded accounts exist in `config.py`.

---

## Enhancement History

All requirement changes are recorded here in reverse-chronological order (newest first).

---

### [2026-05-13] feat: Exclude Senior Management Team + Department Code Display

**Source:** `Dashboard/Requirement/dashboard_department_enhancement_requirement.md`
**Status:** ✅ IMPLEMENTED
**Files changed:** `config.py`, `modules/goal_setting/metrics.py`, `modules/goal_setting/dept_loader.py`, `modules/goal_setting/view.py`

#### Part 1 — Exclude "Senior Management Team"
- `metrics.py:get_effective_df()` now chains two exclusions:
  1. Intern/Collaborator — filters on `Vị trí` (position keyword match)
  2. Senior Management Team — filters on `Phòng ban.strip().lower() == "senior management team"`
- The "Excluded Goal Sheets" KPI now counts both exclusion types combined
- Scope: all KPI, charts, tables, follow-up list (same as Intern exclusion)

#### Part 2 — Department Code Display
- `config.py`: added `HR_STRUCTURE_DATA` path → `Dashboard/Department/HR_structure.xlsx`
- `dept_loader.py`: added `load_hr_structure()` (cached, Sheet1) and `build_dept_name_to_code(hr_df)` → `{dept_name: dept_code}`
- `dept_loader.py:build_filter_options()`: accepts optional `name_to_code` dict; display labels use codes, `display_to_name` mapping still resolves codes → real names (hierarchy/filter logic unchanged)
- `view.py`: both `render_sidebar()` and `render()` load HR structure and pass `_name_to_code` to filter options
- `view.py`: codes applied (display-only) to: Department Progress table, Dept Group Comparison chart, Department Detail Comparison chart
- Fallback: any dept name not in HR_structure renders as the original full name (no crash)

---

### [2026-05-13] Fix: Department Progress column naming + KPI subtitle clarity

**Commit:** `M modules/goal_setting/metrics.py`, `M modules/goal_setting/view.py`
**Type:** Bug fix + UX clarification

#### metrics.py — `compute_department_progress()`
- **Before:** result columns were named `["Department", "Total", "Approved"]`
- **After:** result columns renamed to `["Department", "Total", "Completed"]`
- **Reason:** The column previously used the word "Approved" but it represents all completed statuses (approved + cancelled), which caused semantic confusion downstream.

#### view.py — Completed KPI card subtitle
- **Before:** `f"{kpis['completed_pct']:.2f}% of effective total"`
- **After:** `f"Approved + Cancelled · {kpis['completed_pct']:.2f}% of effective total"`
- **Reason:** Clarifies that "Completed" = E_APPROVED + E_CANCELLED, not just approvals.

---

### [2026-04-29] feat: exclude Intern & Collaborator from Goal Setting KPI and charts

- Added `_EXCLUDED_KEYWORDS = ["intern", "collaborator"]` in `metrics.py`
- Added `get_effective_df(df)` helper that filters on `Vị trí` column
- All KPI, chart, and follow-up computations use `eff_df` (effective dataframe)
- Raw total is still shown in "Excluded Goal Sheets" KPI card with `excluded_count` and `excluded_pct`

---

### [2026-04-29] feat: expand COMPLETED_STATUSES + add Vietnamese aliases

- `COMPLETED_STATUSES` expanded to include `"Đã duyệt"`, `"Approved"`, `"Hủy"`, `"Cancelled"`, `"E_CANCELLED"`
- `_STATUS_LABEL_MAP` in `view.py` updated with full Vietnamese aliases

---

### [2026-04-29] feat: Count+% labels on all charts; follow-up list expanded to all non-completed

- All Plotly bar and pie charts now show `Count (%)` labels on each segment
- Follow-up list (`get_followup_list`) now returns ALL non-COMPLETED_STATUSES rows (not just specific states)

---

### [Earlier] feat: Department hierarchy filtering

- `dept_loader.py` builds a hierarchical tree from the Excel department file
- Sidebar uses `build_filter_options()` to show parent-child labels
- Selecting a parent department auto-expands to all descendant departments via `get_all_descendant_names()`

---

### [Earlier] feat: Dept Group Comparison section

- `compute_dept_group_comparison(df, dept_name_to_group)` added to `metrics.py`
- Renders two charts side-by-side: completion % bar + stacked status bar

---

## Superseded Requirements (do NOT follow these)

| Old requirement | Superseded by | Correct current behaviour |
|---|---|---|
| `pmtool_chart_label_format_requirement.md`: rename column "Completed" → "Approved" | `Enhance logic.md` (2026-05-07) | Column stays **"Completed"** (= Approved + Cancelled) |
| `pmtool_chart_label_format_requirement.md`: E_WAITING_HANDLING → "Awaiting Action" | `Enhance logic.md` (2026-05-07) | Label is **"Not Started"** |
| `pmtool_completion_sort_requirement.md`: Completed = E_APPROVED only | `Enhance logic.md` (2026-05-07) | Completed = **E_APPROVED + E_CANCELLED** |

---

## Implementation Rules

1. **Treat all new requirements as additive enhancements** — do not remove existing features unless explicitly asked.
2. **Preserve backward compatibility** — do not break existing data contracts (column names, JSON shape, API surface).
3. **Avoid destructive refactors** unless explicitly requested.
4. **Append to this file** after every implementation is completed — include date, type, files changed, before/after diff summary.
5. **Exclusion scope** (Intern/Collaborator + Senior Management Team) applies only to Goal Setting KPI/chart computations, not to the raw data load or admin upload flow.
6. **Department filter expansion** is always hierarchical — selecting a parent must include all children.
7. **Department codes are display-only** — all internal aggregation, hierarchy, and filter logic must remain name-based.
