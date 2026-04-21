# Scenario – PM Tool Dashboard System

## Context
The PM Tool project includes multiple phases and business needs, such as:
- Mass Roll-out tracking
- Issue tracking during stabilization
- Future monitoring for other project phases

Currently, project data is managed through raw files.
As the project grows, this makes monitoring fragmented and inefficient.

## Problem
The PM team needs one place to monitor the whole project, but today:
- data is scattered across files
- each tracking need is handled separately
- switching between different views is not efficient
- future expansion will become difficult if the system is not designed properly from the beginning

## Expected Solution
Build one centralized dashboard system for the PM Tool project.

In this system:
- each feature will have its own scenario and its own dashboard logic
- each feature will be displayed as a separate module
- users can switch between modules easily through tabs or toggle view

## Current Modules
### 1. Goal Setting Dashboard
Purpose:
- track Mass Roll-out progress
- monitor completion by department, approver, and status
- identify follow-up priorities

### 2. Issue Tracking Dashboard
Purpose:
- track issue volume and issue status
- monitor severity and issue type
- compare trend across the latest 5 snapshots

## Future Expansion
More modules may be added later, for example:
- Performance Review tracking
- KPI / OKR dashboard
- User adoption monitoring
- SLA / support tracking

Each future feature should have its own scenario, while still using the same centralized dashboard system.

## Expected Outcome
- one tool for the full PM Tool project
- easy switching between dashboards
- easier project control for PM team
- scalable architecture for future features

## Success Criteria
- centralized but modular
- easy to expand
- easy to navigate
- supports daily operation and decision-making
