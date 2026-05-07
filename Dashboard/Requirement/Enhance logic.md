# Goal Setting Dashboard – Enhancement Requirements

> Last updated: 2026-05-07

---

## Part 1 – Exclude Intern & Collaborator Logic

### 1.1 Context
Additional enhancement for position-based filtering. Does NOT replace existing requirements.

### 1.2 Position Exclusion Rule
Exclude records where column `Vị trí` (Position) contains (case-insensitive, partial match):
- "Intern"
- "Collaborator"

Examples:
| Position Value | Excluded? |
| --- | --- |
| Live Operations Collaborator | Yes |
| Customer Service Collaborator | Yes |
| HR Intern | Yes |
| Senior Software Engineer | No |

### 1.3 Effective Dataset
| Metric | Definition |
| --- | --- |
| Raw Total | All uploaded rows |
| Effective Total | Rows EXCLUDING Intern & Collaborator |
| Completion % | Completed / Effective Total |
| Excluded Goal Sheets KPI | Raw Total − Effective Total |

### 1.4 Scope of Exclusion
Exclusion applies to ALL of the following:
- KPI Summary (Completed, In Progress, Not Started, Completion %)
- Status Distribution chart
- Dept Group Comparison
- Department Detail Comparison
- Approver Workload
- Follow-up Required List
- All completion/distribution calculations

---

## Part 2 – Status Mapping Rules

### 2.1 Centralized Status Mapping
All status calculations MUST use the following centralized mapping. No status may appear in more than one group.

#### Not Started
| Raw Status Code | Display Label |
| --- | --- |
| E_WAITING_HANDLING | Not Started |
| Chờ xử lý | Not Started |

#### In Progress
| Raw Status Code | Display Label |
| --- | --- |
| E_WAITING_APPROVE | Awaiting Approval |
| Chờ duyệt | Awaiting Approval |
| E_ADJUST | Awaiting Adjustment |
| Yêu cầu điều chỉnh | Awaiting Adjustment |

#### Completed
| Raw Status Code | Display Label |
| --- | --- |
| E_APPROVED | Approved |
| Đã duyệt | Approved |
| Approved | Approved |
| E_CANCELLED | Cancelled |
| Hủy | Cancelled |
| Cancelled | Cancelled |

### 2.2 Matching Rules
- Case-sensitive exact match on raw status code
- If a status code is not in the mapping, it renders as-is (fallback)

### 2.3 Implementation
Status lists are centralized in `config.py`:
```python
COMPLETED_STATUSES   = ["E_APPROVED", "E_CANCELLED", "Đã duyệt", "Hủy", "Approved", "Cancelled"]
IN_PROGRESS_STATUSES = ["E_WAITING_APPROVE", "E_ADJUST", "Chờ duyệt", "Yêu cầu điều chỉnh"]
NOT_STARTED_STATUSES = ["E_WAITING_HANDLING", "Chờ xử lý"]
```

Display label mapping is centralized in `modules/goal_setting/view.py` (`_STATUS_LABEL_MAP`).

---

## Part 3 – Chart & KPI Display Rules

### 3.1 KPI Summary
| KPI Card | Value | Subtitle |
| --- | --- | --- |
| Total Goal Sheets | Effective Total count | — |
| Completed | Count of Completed records | X.XX% of effective total |
| In Progress | Count of In Progress records | X.XX% of effective total |
| Not Started | Count of Not Started records | X.XX% of effective total |
| Excluded Goal Sheets | Count of excluded records | X.XX% of raw total |

### 3.2 All Charts
- Every chart/table MUST display both **Count** and **Percentage (%)**
- Percentage format: **2 decimal places** (e.g., `12.34%`)
- Count and % MUST use the same dataset and calculation
- Intern/Collaborator records MUST NOT be included in any percentage

### 3.3 Goal Sheet Status Distribution Chart
- MUST display distribution by mapped display status (aggregated)
- Bar label format: `Count (X.XX%)`
- Uses effective dataset (Intern/Collaborator excluded)

### 3.4 Dept Group & Department Detail Comparison
- Bar chart label: `Completed / Total (X.XX%)`
- Stacked bar label: `Count (X.XX%)`
- Percentage denominator = dept/group total (effective)

### 3.5 Approver Workload
- Columns: Approver, Total, Pending, Completion%
- Completion% = Approved / Total × 100, rounded to 2 decimal places

---

## Part 4 – Follow-up Required List

### 4.1 Definition
Shows all goal sheets where status is NOT in COMPLETED_STATUSES (i.e., not Approved or Cancelled).

### 4.2 Columns
| Column | Source |
| --- | --- |
| Employee | Nhân viên |
| Department | Phòng ban |
| Status | Trạng thái (mapped to display label) |
| Approver | Người duyệt |

### 4.3 Behavior
- Follows all active sidebar filters (Department, Approver, Status)
- Intern/Collaborator records excluded
- Supports sorting and filtering via Streamlit dataframe
- Header shows: `N require follow-up (X.XX% of effective total)`

---

## Acceptance Criteria

| ID | Criteria |
| --- | --- |
| AC01 | Position containing "Intern" is excluded from all KPI and chart calculations |
| AC02 | Position containing "Collaborator" is excluded from all KPI and chart calculations |
| AC03 | Position matching is case-insensitive and partial |
| AC04 | Excluded Goal Sheets KPI is displayed with count and % of raw total |
| AC05 | E_WAITING_HANDLING and Chờ xử lý are both counted as Not Started |
| AC06 | E_WAITING_APPROVE, E_ADJUST, Chờ duyệt, Yêu cầu điều chỉnh are counted as In Progress |
| AC07 | E_APPROVED, E_CANCELLED, Đã duyệt, Hủy, Approved, Cancelled are counted as Completed |
| AC08 | No status appears in more than one group |
| AC09 | Completion % = Completed / Effective Total |
| AC10 | All charts show Count and Percentage with 2 decimal places |
| AC11 | Status Distribution chart aggregates display labels before rendering |
| AC12 | Sidebar status filter correctly expands display label to all matching raw codes |
| AC13 | Follow-up list shows all non-completed records (excludes Approved and Cancelled) |
| AC14 | All existing filters continue working correctly |
| AC15 | Dept Group and Department Detail comparison use effective dataset |
