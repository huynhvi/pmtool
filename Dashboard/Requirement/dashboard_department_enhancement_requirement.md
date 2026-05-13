# Goal Setting Dashboard – Additional Enhancement Requirement

> This requirement is ADDITIVE ONLY.  
> DO NOT overwrite existing logic or requirements.

---

# Part 1 – Exclude Senior Management Team

## 1.1 Exclusion Rule

Exclude all records where department name is:

`Senior Management Team`

Matching rule:
- trim whitespace
- case-insensitive exact match

Example:
```python
department.strip().lower() == "senior management team"
```

---

## 1.2 Scope of Exclusion

This exclusion MUST apply to ALL:

- KPI Summary
- Goal Sheet Status Distribution
- Dept Group Comparison
- Department Detail Comparison
- Approver Workload
- Follow-up Required List
- All percentages
- All chart calculations
- All exported datasets used by dashboard

---

## 1.3 Effective Dataset Update

Effective dataset =
- existing filtered dataset
- excluding Intern / Collaborator
- excluding Senior Management Team

All dashboard metrics MUST use this final effective dataset.

---

# Part 2 – Department Code Display Enhancement

## 2.1 Additional Data Source

Read organization mapping from:

`HR_structure`

Required columns:

| Column | Purpose |
|---|---|
| Mã phòng ban | Department code |
| Tên phòng ban | Department name |

---

## 2.2 Mapping Logic

Build mapping:

```python
department_name -> department_code
```

Example:

| Department Name | Department Code |
|---|---|
| Human Resource | HR |
| Finance Planning | FP&A |

---

## 2.3 Display Rules

Dashboard MUST display:

`Mã phòng ban`

instead of full department name in:

- Department filter
- Dept Group Comparison
- Department Detail Comparison
- Tables
- Charts
- Tooltips
- Export datasets

---

## 2.4 Calculation Rules

IMPORTANT:
- Existing aggregation/filter/hierarchy logic SHOULD continue using current internal department structure logic
- Department code is DISPLAY ONLY unless current architecture safely supports code-based aggregation

Purpose:
- avoid breaking existing hierarchy/filter logic

---

## 2.5 Fallback Logic

If mapping is missing:
- fallback to original department name
- dashboard MUST NOT fail

Example:
```python
display_department = dept_code if dept_code else department_name
```
