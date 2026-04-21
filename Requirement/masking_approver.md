# Masking Approver

### 4.4 Additional Requirement – Approver Name Masking

In addition to employee name masking, the system must also apply masking to the "Approver" field.

#### Requirement
- Approver names must be masked before displaying on dashboard
- The same masking rule must be applied as employee names

#### Masking Rule
- keep last name (given name) fully visible
- for other parts:
  - keep first letter only
  - format as abbreviation

Example:
- Nguyen Van Anh → N. V. Anh
- Tran Thi Bich → T. T. Bich

#### Usage
- Dashboard must use masked Approver names only
- Raw Approver names must NOT be displayed

#### Scope
- Applies to:
  - Mass Rollout Dashboard
  - any future module displaying Approver data

#### Purpose
- ensure data privacy
- maintain consistency in data masking across all personal fields