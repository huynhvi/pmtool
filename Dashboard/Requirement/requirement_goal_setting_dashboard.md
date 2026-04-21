# Requirement – Goal Setting Dashboard

## 1. Scope
Build a simple single-page dashboard to track Goal Setting progress during Mass Roll-out.

---

## 2. Input
Upload Excel file (.xlsx)

Required columns:
- Employee
- Department
- Status
- Approver

---

## 3. Dashboard Structure

### 3.1 KPI Summary
Display 4 metrics:
- Total goal sheets
- Completed
- Not-started
- In-progress

---

### 3.2 Status Overview
Chart:
- Number of goal sheets by status

Purpose:
- Identify where the process is blocked

---

### 3.3 Department Progress
Table:

| Department | Total | Completed | Completion % |

Rule:
- Highlight low completion departments

---

### 3.4 Approver Workload
Table:

| Approver | Total | Pending | Completion % |

Purpose:
- Identify bottleneck approvers

---

### 3.5 Follow-up List
Table:

Show employees requiring follow-up

Default:
- Status = E_WAITING_HANDLING

---

## 4. Metric Logic

- Total = total rows
- Not-started = status == E_WAITING_HANDLING
- Completed = configurable status group
- In-progress = Total - Completed - Not-started
- Completion rate = Completed / Total

---

## 5. Filters

### 5.1 Filter Fields
- Department (multi-select)
- Approver (multi-select)
- Status (multi-select)

### 5.2 Behavior
- User can select one or more values per filter
- Selecting no values = show all (same as "All")
- Dashboard updates instantly when selection changes
- All filters active simultaneously (AND logic)

### 5.3 Default State
- No values pre-selected → all data shown

---

## 6. System Behavior
- Upload file → auto refresh dashboard
- No manual reload required
- Single page only

---

## 7. Non-functional Requirements
- Fast loading
- Simple UI
- Easy to maintain
- No over-engineering

---

## 8. Design Principles
- Prioritize readability
- Prioritize actionability
- Keep it simple
