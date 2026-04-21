# Requirement – Chart Label Standardization & Data Formatting

## 1. Goal Sheet Status Distribution – Label Update

The system must standardize status labels displayed on the chart.

### Mapping Rules:

| Raw Status | Display Label |
|-----------|--------------|
| E_ADJUST | Awaiting Adjustment |
| E_APPROVED | Approved |
| E_WAITING_APPROVE | Awaiting Approval |
| E_WAITING_HANDLING | Awaiting Action |

### Requirement:
- Dashboard must NOT display raw status values
- Only display standardized labels as defined above

---

## 2. Detailed Breakdown Table – Column Update

### 2.1 Column Name Update
- Rename column:
  - "Completed" → "Approved"

### 2.2 Completion Percentage Format

- Completion % must:
  - display with **2 decimal places**
  - format example:
    - 85.236% → 85.24%
    - 90% → 90.00%

### Requirement:
- Values must be rounded to 2 decimal places
- Ensure consistent formatting across all tables

---

## 3. Purpose

- improve readability for business users
- ensure consistency between system data and UI display
- avoid confusion from raw status naming
