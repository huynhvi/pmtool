# Requirement – Issue Tracking Dashboard

## 1. Scope
Build a dashboard module to track and analyze issues during and after PM Tool rollout.

The dashboard must:
- read raw data from Excel
- calculate issue metrics
- visualize issue distribution
- track issue trends over time
- support objective evaluation for system health

## 2. Input

### 2.1 Data Source
- Excel file (.xlsx)
- Data must be read from sheet:
  → "IssuesLog"

### 2.2 Data Handling
- The system must:
  - read data from the specified sheet
  - detect and extract relevant columns
  - normalize data before calculation

## 3. Metrics

### 3.1 Total Issues
- Total number of issues in dataset

### 3.2 Issue Status Breakdown
Count issues by status:
- Open
- Reopen
- Closed
- To Confirm

### 3.3 Severity Breakdown (Open)
Count issues where:
- Status = Open

Group by severity:
- High
- Medium
- Low

### 3.4 Severity Breakdown (Reopen)
Count issues where:
- Status = Reopen

Group by severity:
- High
- Medium
- Low

### 3.5 Issue Type (Open + Reopen)
Count issues where:
- Status = Open OR Reopen

Group by type:
- Bug
- Configuration
- Improvement

## 4. Trend Tracking (Critical Requirement)

### 4.1 Scope
The system must compare the latest 5 snapshots.

Each snapshot represents a dataset at a specific time.

### 4.2 Metrics for Comparison
Track trend for:
- Total Issues
- Open Issues
- Reopen Issues

### 4.3 Calculation
For each metric:

% Change = (Current - Previous) / Previous

### 4.4 Visualization
- Line chart (for trend)
- KPI delta indicator (increase / decrease)

## 5. Evaluation Logic (Important)

The system must provide objective evaluation based on percentage change.

### 5.1 Rules

- If Open or Reopen increases:
  → Risk level increases

- If Open or Reopen decreases:
  → System is stabilizing

- If High severity exists in Open/Reopen:
  → Mark as critical risk

### 5.2 Output Format

For each key metric:
- show % increase / decrease
- show trend direction:
  - ↑ increase
  - ↓ decrease

- provide short evaluation:
  Example:
  - "Open issues increased by 15% → risk is rising"
  - "Reopen issues decreased by 20% → quality is improving"

## 6. Dashboard Output

### 6.1 KPI Summary
- Total Issues
- Open
- Reopen
- High severity (Open + Reopen)

### 6.2 Status Distribution
- Chart: Issue count by status

### 6.3 Severity Distribution
- Chart:
  - Open (High / Medium / Low)
  - Reopen (High / Medium / Low)

### 6.4 Issue Type Distribution
- Chart: Bug / Configuration / Improvement

### 6.5 Trend View
- Line chart (last 5 snapshots)
- % change indicator

## 7. Data Processing Rules

The system must:
- map status values consistently:
  - normalize "Open", "OPEN", etc.
- map severity values:
  - High / Medium / Low
- map issue types:
  - Bug / Configuration / Improvement

## 8. Error Handling

If required data is missing:
- system must:
  - flag missing fields
  - show warning
  - avoid incorrect calculation

## 9. Design Principle

- Focus on clarity and actionability
- Avoid over-complex visualization
- Highlight risks clearly
- Support quick decision-making