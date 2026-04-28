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

## 5. Department Comparison Charts

### 5.1 Purpose

Enable comparison across the organization structure at two levels:

1. **Dept Group level**: compare progress between parent department groups.
2. **Department detail level**: compare progress between individual departments / child departments.

This helps stakeholders identify:

- Low-performing department groups
- Low-performing individual departments
- Bottlenecks by organization layer
- Priority follow-up groups

---

### 5.2 Required Charts

System must provide **two separate comparison charts**:

| Chart | Level | Purpose |
|---|---|---|
| Dept Group Comparison | Parent department group level | Compare progress between Dept Groups |
| Department Detail Comparison | Individual department / child department level | Compare progress between detailed departments |

---

### 5.3 Chart 1 – Dept Group Comparison

#### Chart Name

**Dept Group Comparison**

#### Description

This chart compares goal setting progress across **Dept Groups**.

A Dept Group is identified from Department data where:

- `type = DEPT_GROUP`

#### Data Mapping Rule

For each Dept Group:

- Include all goal sheets that belong to departments under that Dept Group.
- The system must include all child departments / teams under the selected Dept Group hierarchy.
- Aggregation must be based on the department hierarchy using `code` and `parent_code`.

#### Metrics

| Metric | Description |
|---|---|
| Total | Total goal sheets under the Dept Group |
| Completed | Completed sheets under the Dept Group |
| Not-started | Waiting handling sheets under the Dept Group |
| In-progress | Remaining sheets under the Dept Group |
| Completion % | Completed / Total |

#### Recommended Chart Types

Option 1 – Bar Chart:
- X-axis: Dept Group
- Y-axis: Completion %

Option 2 – Stacked Bar Chart:
- X-axis: Dept Group
- Y-axis: Number of goal sheets
- Breakdown by Completed / In-progress / Not-started

---

### 5.4 Chart 2 – Department Detail Comparison

#### Chart Name

**Department Detail Comparison**

#### Description

This chart keeps the existing detailed comparison across individual departments / child departments.

It must remain available even after adding the Dept Group Comparison chart.

#### Data Mapping Rule

For each department:

- Show progress at individual department / child department level.
- Do not aggregate multiple departments into one group in this chart.
- If a filter is applied at Dept Group level, this chart should show only departments under the selected Dept Group.

#### Metrics

| Metric | Description |
|---|---|
| Total | Total goal sheets of the department |
| Completed | Completed sheets of the department |
| Not-started | Waiting handling sheets of the department |
| In-progress | Remaining sheets of the department |
| Completion % | Completed / Total |

#### Recommended Chart Types

Option 1 – Bar Chart:
- X-axis: Department
- Y-axis: Completion %

Option 2 – Stacked Bar Chart:
- X-axis: Department
- Y-axis: Number of goal sheets
- Breakdown by Completed / In-progress / Not-started

---

### 5.5 Filter Interaction

Both comparison charts must follow the active filter logic:

- Department / Dept Group filter
- Approver filter
- Status filter

Rules:

- If no Dept Group / Department filter is selected, both charts show all available data.
- If a Dept Group is selected:
  - Dept Group Comparison reflects the selected Dept Group scope.
  - Department Detail Comparison shows only departments under the selected Dept Group.
- If one or more child departments are selected:
  - Department Detail Comparison shows only selected departments.
  - Dept Group Comparison aggregates the selected departments back to their corresponding Dept Group.
- No duplicate records are allowed when parent and child departments are selected together.

---

## 6. Dashboard Structure Update

Add two new sections:

### 6.1 Dept Group Comparison

Chart:
- Compare progress across Dept Groups

Display:
- Completion % by Dept Group
- Status distribution by Dept Group

Purpose:
- Identify low-progress Dept Groups
- Support management-level follow-up and escalation

---

### 6.2 Department Detail Comparison

Chart:
- Compare progress across individual departments / child departments

Display:
- Completion % by department
- Status distribution by department

Purpose:
- Keep detailed department-level comparison
- Identify specific departments that require follow-up

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
| AC07 | Dept Group Comparison chart is displayed as a separate chart |
| AC08 | Department Detail Comparison chart is still displayed and not removed |
| AC09 | Dept Group Comparison correctly aggregates all child departments under each Dept Group |
| AC10 | Department Detail Comparison shows individual departments / child departments |
| AC11 | Both comparison charts correctly reflect filtered data |
| AC12 | All filters work together (AND logic) |

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
- Build two aggregation levels:
  - Dept Group level aggregation
  - Department detail level aggregation
- Ensure both comparison charts update instantly with filters
