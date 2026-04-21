# Tracking SC

# Scenario – Issue Tracking Dashboard

## Context
After Mass Roll-out, the PM Tool enters the operation and stabilization phase.
At this stage, issue tracking becomes critical to ensure system quality and rollout readiness.

Besides tracking Goal Setting progress, the PM team needs a separate dashboard to monitor issues across upcoming phases.

## Problem
Currently, issue data exists in raw files but:
- No centralized dashboard to monitor issue status
- No clear visibility of issue severity (High/Medium/Low)
- No tracking of issue types (Bug / Configuration / Improvement)
- No historical comparison to evaluate trend (increase / decrease)

→ This makes it difficult to:
- assess system health
- track issue resolution performance
- support decision-making for rollout readiness

## Expected Solution
A simple dashboard that:
- reads raw Excel file
- calculates issue metrics automatically
- displays issue distribution clearly
- shows trend across recent snapshots

## Key Metrics to Track

### 1. Total Issues
- Total number of issues in the dataset

### 2. Issue Status
- Open
- Reopen
- Closed
- To Confirm

### 3. Issue Severity (Open)
- High
- Medium
- Low

### 4. Issue Severity (Reopen)
- High
- Medium
- Low

### 5. Issue Type (Open + Reopen)
- Bug
- Configuration
- Improvement

## Trend Tracking (Critical)
The dashboard must compare the latest 5 snapshots:
- Show % increase / decrease for:
  - Total issues
  - Open issues
  - Reopen issues

## Daily Usage
PM will:
- check total issue volume
- monitor open/reopen backlog
- identify high severity risks
- track issue trend vs previous snapshots

## Expected Outcome
- Understand system health quickly
- Identify risk before rollout phases
- Support decision on rollout readiness

## Success Criteria
- Clear issue breakdown
- Visible trend (increase/decrease %)
- Easy to interpret without deep analysis