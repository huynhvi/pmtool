# Goal Setting Dashboard – Enhancement Requirement (Add-on)

## 1. Context

This document defines **additional requirements** to enhance the existing Goal Setting Dashboard.

These updates **DO NOT replace** existing requirements. They extend current functionality.

---

## 2. Enhancement Scope

### 2.1 Department Filter Enhancement  
### 2.2 Department Comparison Chart

---

## 3. Additional Input Data

### 3.1 Department Data Source

System must read department structure from:

- Source: **"Department"**
- Format: Excel / data source

### 3.2 Required Fields

| Field | Description |
|---|---|
| code | Department code |
| name | Department name |
| type | DEPT_GROUP / DEPT / TEAM |
| parent_code | Parent department code |
| manager | Department manager |

---

## 4. Department Filter Enhancement

### 4.1 Current Behavior

- Filter only supports selecting **single child department**
- No hierarchy support

---

### 4.2 New Behavior

Department filter must support **hierarchical filtering**

#### Supported Selection Types

| Selection Type | Behavior |
|---|---|
| Parent Department | Include ALL child departments |
| Child Department | Only that department |
| Multiple selections | Combine all selections |
| No selection | Show all data |

---

### 4.3 Filter Logic

- Use `code` and `parent_code` to build hierarchy
- When selecting a parent:
  → Automatically include all descendants
- When selecting both parent + child:
  → MUST NOT duplicate data
- Combine with other filters using **AND logic**

---

### 4.4 Expected UX Behavior

- Multi-select dropdown
- Display hierarchy clearly (optional: tree view)
- Fast response when filtering

---

## 5. Department Comparison Chart

### 5.1 Purpose

Enable comparison across departments to identify:

- Low-performing departments
- Bottlenecks
- Priority follow-up groups

---

### 5.2 Chart Name

**Department Comparison**

---

### 5.3 Metrics

For each department:

| Metric | Description |
|---|---|
| Total | Total goal sheets |
| Completed | Completed sheets |
| Not-started | Waiting handling |
| In-progress | Remaining |
| Completion % | Completed / Total |

---

### 5.4 Chart Types

System should support:

#### Option 1 – Bar Chart
- X-axis: Department
- Y-axis: Completion %

#### Option 2 – Stacked Bar Chart
- Breakdown by:
  - Completed
  - In-progress
  - Not-started

---

## 6. Dashboard Structure Update

Add new section:

### Department Comparison

Chart:
- Compare progress across departments

Display:
- Completion % by department
- Status distribution by department

Purpose:
- Identify low-performance departments
- Support escalation & follow-up

---

## 7. Acceptance Criteria

| ID | Criteria |
|---|---|
| AC01 | System reads Department data successfully |
| AC02 | Filter displays both parent & child departments |
| AC03 | Selecting parent includes all children |
| AC04 | Selecting child shows only that department |
| AC05 | Multi-select works correctly |
| AC06 | No duplicate data when selecting parent + child |
| AC07 | Department Comparison chart is displayed |
| AC08 | Chart correctly reflects filtered data |
| AC09 | All filters work together (AND logic) |

---

## 8. Non-functional Requirements

- Fast filtering response
- Clean UI
- No over-engineering
- Maintain compatibility with existing dashboard

---

## 9. Implementation Notes (For Claude)

- Treat Department as **hierarchical data**
- Preprocess department tree before filtering
- Cache hierarchy for performance
- Ensure chart updates instantly with filters
