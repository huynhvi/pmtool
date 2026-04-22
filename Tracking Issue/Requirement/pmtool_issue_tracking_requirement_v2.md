# Requirement – Issue Tracking Dashboard

## 1. Scope
Build an Issue Tracking Dashboard module for PM Tool.

The module must:
- read source data from Excel
- generate a standardized raw data snapshot
- create dashboard views from the generated raw data
- compare the latest 5 snapshots
- provide objective trend evaluation based on percentage change

---

## 2. Input Source

### 2.1 Source File
- Input format: Excel (.xlsx)

### 2.2 Source Sheet
- The system must read issue data from sheet:
  - "IssuesLog"

---

## 3. Processing Flow

The system must follow this process:

1. Read issue data from sheet "IssuesLog"
2. Extract and normalize required fields
3. Aggregate the data into a standardized raw data snapshot file
4. Save the snapshot file
5. Use the snapshot data as the source for dashboard generation
6. Compare the latest 5 snapshot files for history tracking

---

## 4. Raw Data Snapshot Requirement

### 4.1 Snapshot File Name Format
The generated raw data snapshot file must follow this naming convention:

- Rawdata_yyyymmdd_hhmmss

Example:
- Rawdata_20260422_103000

### 4.2 Purpose
The snapshot file is the standardized data source used for:
- dashboard rendering
- historical comparison
- trend evaluation

---

## 5. Raw Data Snapshot Content

Each generated snapshot must contain the following aggregated metrics:

### 5.1 Total Issues
- Total number of issues

### 5.2 Issue Status Summary
For each status below, the system must store:
- issue count
- percentage based on total number of issues

Statuses:
- Open
- Reopen
- Closed
- To Confirm

### 5.3 Severity Summary for Open Issues
For each severity below, the system must store:
- issue count
- percentage based on total number of issues

Condition:
- Status = Open

Severities:
- High
- Medium
- Low

### 5.4 Severity Summary for Reopen Issues
For each severity below, the system must store:
- issue count
- percentage based on total number of issues

Condition:
- Status = Reopen

Severities:
- High
- Medium
- Low

### 5.5 Issue Type Summary for Open + Reopen
For each issue type below, the system must store:
- issue count
- percentage based on total number of issues

Condition:
- Status = Open OR Reopen

Types:
- Bug
- Configuration
- Improvement

---

## 6. Dashboard Data Source

The dashboard must use the generated raw data snapshot as its data source.

The dashboard must NOT directly calculate metrics from the original uploaded file after snapshot generation.

---

## 7. Dashboard Output

### 7.1 KPI Summary
Display at least:
- Total Issues
- Open
- Reopen
- Closed
- To Confirm

### 7.2 Status Summary
Display issue count and percentage for:
- Open
- Reopen
- Closed
- To Confirm

### 7.3 Severity Summary
Display issue count and percentage for:
- Open → High / Medium / Low
- Reopen → High / Medium / Low

### 7.4 Issue Type Summary
Display issue count and percentage for:
- Bug
- Configuration
- Improvement

Condition:
- based on Open + Reopen only

---

## 8. History Tracking (Critical Requirement)

### 8.1 Scope
The dashboard must compare the latest 5 generated raw data snapshots.

### 8.2 Comparison Target
The system must show increase / decrease trend for at least:
- Total Issues
- Open
- Reopen
- Closed
- To Confirm

The system should also support trend comparison for:
- Open severity distribution
- Reopen severity distribution
- Open + Reopen type distribution

### 8.3 Calculation Rule
Trend must be recorded by percentage change.

Formula:
- % Change = (Current Snapshot - Previous Snapshot) / Previous Snapshot

### 8.4 Display Requirement
History view must:
- compare the latest 5 snapshots
- show increase / decrease direction
- display percentage change clearly

Example:
- Open increased by 12.50%
- Reopen decreased by 8.33%

---

## 9. Objective Evaluation Requirement

The dashboard must provide objective evaluation together with the trend.

### 9.1 Evaluation Principle
Evaluation must be based on percentage change, not on subjective comments only.

### 9.2 Evaluation Examples
- If Open increases → risk is increasing
- If Reopen increases → quality risk is increasing
- If Open decreases → issue backlog is improving
- If Reopen decreases → quality stability is improving

### 9.3 Output Style
Evaluation text should be:
- short
- clear
- objective
- business-friendly

Example:
- "Open issues increased by 12.50% compared to the previous snapshot, indicating rising backlog risk."
- "Reopen issues decreased by 10.00%, showing improvement in issue resolution quality."

---

## 10. Data Normalization Rules

The system must normalize values before aggregation, including:
- status values
- severity values
- issue type values

Examples:
- OPEN → Open
- reopen → Reopen
- HIGH → High

---

## 11. Error Handling

If required data cannot be extracted from sheet "IssuesLog", the system must:
- stop snapshot generation
- flag missing or invalid fields
- avoid creating misleading dashboard data

---

## 12. Design Principle

- snapshot-based processing
- clear and auditable metric generation
- objective trend evaluation
- simple and readable dashboard output
## 13. Snapshot Schema Compliance (Critical)

### 13.1 Schema Alignment

The generated raw data snapshot MUST strictly follow the predefined schema:

- File structure must include:
  - Sheet: "Summary"
  - Sheet: "Metadata"

- Column structure in "Summary" must include:
  - Snapshot_ID
  - Snapshot_Date
  - Metric_Group
  - Metric_Subgroup
  - Metric_Name
  - Metric_Count
  - Metric_Percentage
  - Base_Total_Issues

### 13.2 Metric Mapping to Schema

All metrics must be stored using the following mapping:

#### Total Issues
- Metric_Group = "Total_Issues"
- Metric_Name = "Total Issues"

#### Status Metrics
- Metric_Group = "Status"
- Metric_Name = Open / Reopen / Closed / To Confirm

#### Open Severity
- Metric_Group = "Open_Severity"
- Metric_Name = High / Medium / Low

#### Reopen Severity
- Metric_Group = "Reopen_Severity"
- Metric_Name = High / Medium / Low

#### Issue Type (Open + Reopen)
- Metric_Group = "Open_Reopen_Type"
- Metric_Name = Bug / Configuration / Improvement

### 13.3 Dashboard Data Binding

The dashboard must:
- read data from "Summary" sheet only
- use:
  - Metric_Group
  - Metric_Name
  - Metric_Count
  - Metric_Percentage

- use Snapshot_ID or Snapshot_Date for:
  - history comparison
  - trend calculation

### 13.4 Consistency Requirement

All generated snapshots must:
- follow the same schema structure
- use consistent naming for Metric_Group and Metric_Name
- ensure Base_Total_Issues is identical across all rows in the same snapshot

### 13.5 Validation Requirement

Before saving snapshot, system must validate:
- schema structure is correct
- required columns exist
- metric values are valid
- percentage values are correctly calculated

If validation fails:
- snapshot must NOT be saved
- system must return error