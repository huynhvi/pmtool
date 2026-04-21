# Requirement – Completion Logic & Sorting

## 1. Objective
Define clear completion logic and default sorting behavior for Mass Rollout Dashboard.

---

## 2. Completion Definition (Important)

A goal sheet is considered **Completed** when:
- Status = "Approved"

---

## 3. Completion Metric Calculation

- Completed = count of goal sheets where Status = "E_APPROVED"
- Completion Rate = Completed / Total Goal Sheets

---

## 4. Sorting Requirement

### Default Sorting Rule:
- Sort by **Completion Rate (descending)**
- Highest completion rate → shown at the top
- Lowest completion rate → shown at the bottom

---

## 5. Scope

This rule applies to:
- Department Progress table
- Any table displaying completion rate

---

## 6. Purpose

- highlight high-performing departments
- identify low-performing areas quickly
- support faster decision-making
