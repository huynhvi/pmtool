# Schema – Issue Tracking Raw Data Snapshot

## 1. Objective
Define the standardized schema for the generated raw data snapshot file used by the Issue Tracking Dashboard.

This schema is used after the system reads source data from sheet `IssuesLog` and aggregates the required metrics.

---

## 2. File Naming Convention

The generated snapshot file must follow this format:

- `Rawdata_yyyymmdd_hhmmss`

Example:
- `Rawdata_20260422_103000`

---

## 3. File Purpose

The snapshot file is the processed and standardized data source for:
- dashboard rendering
- historical comparison
- trend calculation
- objective evaluation

The dashboard must read from this snapshot file, not directly from the uploaded source file.

---

## 4. Recommended File Structure

The snapshot file should contain 2 sheets:

### Sheet 1: `Summary`
Stores the aggregated metrics for the current snapshot.

### Sheet 2: `Metadata`
Stores snapshot metadata for traceability and audit.

---

## 5. Sheet Schema

# 5.1 Sheet: Summary

Each row in the `Summary` sheet represents one metric item.

Recommended columns:

| Column Name | Data Type | Required | Description |
|------------|-----------|----------|-------------|
| Snapshot_ID | string | Yes | Unique snapshot identifier, usually same as file timestamp |
| Snapshot_Date | datetime | Yes | Snapshot creation date and time |
| Metric_Group | string | Yes | Main metric category |
| Metric_Subgroup | string | No | Sub-category if applicable |
| Metric_Name | string | Yes | Specific metric label |
| Metric_Count | integer | Yes | Count value for the metric |
| Metric_Percentage | decimal(5,2) | No | Percentage value based on total issues |
| Base_Total_Issues | integer | Yes | Total issue count used as denominator |
| Notes | string | No | Optional note |

---

### 5.1.1 Allowed Values

#### `Metric_Group`
Allowed values:
- Total_Issues
- Status
- Open_Severity
- Reopen_Severity
- Open_Reopen_Type

#### `Metric_Subgroup`
Examples:
- Status
- Severity
- Type

#### `Metric_Name`
Examples:
- Total Issues
- Open
- Reopen
- Closed
- To Confirm
- High
- Medium
- Low
- Bug
- Configuration
- Improvement

---

### 5.1.2 Summary Sheet Example

| Snapshot_ID | Snapshot_Date | Metric_Group | Metric_Subgroup | Metric_Name | Metric_Count | Metric_Percentage | Base_Total_Issues | Notes |
|------------|---------------|--------------|-----------------|-------------|--------------|-------------------|-------------------|-------|
| 20260422_103000 | 2026-04-22 10:30:00 | Total_Issues |  | Total Issues | 120 | 100.00 | 120 |  |
| 20260422_103000 | 2026-04-22 10:30:00 | Status | Status | Open | 30 | 25.00 | 120 |  |
| 20260422_103000 | 2026-04-22 10:30:00 | Status | Status | Reopen | 10 | 8.33 | 120 |  |
| 20260422_103000 | 2026-04-22 10:30:00 | Status | Status | Closed | 70 | 58.33 | 120 |  |
| 20260422_103000 | 2026-04-22 10:30:00 | Status | Status | To Confirm | 10 | 8.33 | 120 |  |
| 20260422_103000 | 2026-04-22 10:30:00 | Open_Severity | Severity | High | 8 | 6.67 | 120 | Status = Open |
| 20260422_103000 | 2026-04-22 10:30:00 | Open_Severity | Severity | Medium | 15 | 12.50 | 120 | Status = Open |
| 20260422_103000 | 2026-04-22 10:30:00 | Open_Severity | Severity | Low | 7 | 5.83 | 120 | Status = Open |
| 20260422_103000 | 2026-04-22 10:30:00 | Reopen_Severity | Severity | High | 3 | 2.50 | 120 | Status = Reopen |
| 20260422_103000 | 2026-04-22 10:30:00 | Reopen_Severity | Severity | Medium | 4 | 3.33 | 120 | Status = Reopen |
| 20260422_103000 | 2026-04-22 10:30:00 | Reopen_Severity | Severity | Low | 3 | 2.50 | 120 | Status = Reopen |
| 20260422_103000 | 2026-04-22 10:30:00 | Open_Reopen_Type | Type | Bug | 20 | 16.67 | 120 | Status in Open/Reopen |
| 20260422_103000 | 2026-04-22 10:30:00 | Open_Reopen_Type | Type | Configuration | 12 | 10.00 | 120 | Status in Open/Reopen |
| 20260422_103000 | 2026-04-22 10:30:00 | Open_Reopen_Type | Type | Improvement | 8 | 6.67 | 120 | Status in Open/Reopen |

---

# 5.2 Sheet: Metadata

Stores metadata about how the snapshot was created.

Recommended columns:

| Column Name | Data Type | Required | Description |
|------------|-----------|----------|-------------|
| Snapshot_ID | string | Yes | Unique snapshot identifier |
| Snapshot_Date | datetime | Yes | Snapshot creation date and time |
| Source_File_Name | string | Yes | Original uploaded file name |
| Source_Sheet_Name | string | Yes | Source sheet name, expected = `IssuesLog` |
| Total_Source_Rows | integer | Yes | Total rows read from source |
| Processed_By | string | No | System / admin / service name |
| Processing_Status | string | Yes | Success / Failed |
| Error_Message | string | No | Error details if processing failed |

---

### 5.2.1 Metadata Sheet Example

| Snapshot_ID | Snapshot_Date | Source_File_Name | Source_Sheet_Name | Total_Source_Rows | Processed_By | Processing_Status | Error_Message |
|------------|---------------|------------------|-------------------|-------------------|--------------|-------------------|---------------|
| 20260422_103000 | 2026-04-22 10:30:00 | Go-live Issue Tracker.xlsx | IssuesLog | 120 | system | Success |  |

---

## 6. Calculation Rules

### 6.1 Base Total
- `Base_Total_Issues` = total number of issues in the snapshot

### 6.2 Percentage Formula
- `Metric_Percentage = Metric_Count / Base_Total_Issues * 100`

### 6.3 Format Rule
- Store percentage with 2 decimal places

Example:
- 12.5 → 12.50
- 8.3333 → 8.33

---

## 7. Metric Mapping Rules

### 7.1 Status Metrics
Include:
- Open
- Reopen
- Closed
- To Confirm

### 7.2 Open Severity Metrics
Condition:
- Status = Open

Include:
- High
- Medium
- Low

### 7.3 Reopen Severity Metrics
Condition:
- Status = Reopen

Include:
- High
- Medium
- Low

### 7.4 Open + Reopen Type Metrics
Condition:
- Status in (Open, Reopen)

Include:
- Bug
- Configuration
- Improvement

---

## 8. Validation Rules

The system must validate:
- snapshot file name format is correct
- `Summary` sheet exists
- `Metadata` sheet exists
- `Base_Total_Issues` is consistent across all rows in the same snapshot
- `Metric_Count` is integer
- `Metric_Percentage` is decimal with 2 digits
- `Source_Sheet_Name` = `IssuesLog`

---

## 9. Usage Rule for Dashboard

The dashboard must:
- read data from the `Summary` sheet
- use `Snapshot_ID` and `Snapshot_Date` for history comparison
- compare the latest 5 snapshots only

The dashboard must not read directly from the original uploaded issue file once the snapshot has been generated.

---

## 10. Design Principle

- simple structure
- easy for AI to parse
- easy for dashboard to consume
- supports audit and history tracking
