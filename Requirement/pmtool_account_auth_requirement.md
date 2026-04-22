# Account & Authorization Requirement

## 1. Objective
Provide predefined system accounts and role-based access control for initial system usage and testing.

---

## 2. Predefined Accounts

The system must support the following default accounts:

### 2.1 Admin Account
- Account: Admins
- Password: Admin@41+
- Role: Admin

### 2.2 User Account
- Account: Usr
- Password: uSR@2226***
- Role: User

---

## 3. Role Definition

### 3.1 Admin Role
Admin users can:
- access Data Processing Layer
- upload raw data files
- trigger data parsing and transformation
- manage system data
- access dashboards

---

### 3.2 User Role
User accounts can:
- access Dashboard Layer only
- view dashboards
- cannot upload data
- cannot access raw data

---

## 4. Login Behavior

- Users must log in using predefined accounts
- System must assign role based on account
- After login:
  - Admin → access Admin + Dashboard
  - User → access Dashboard only

---

## 5. Security Note (Important)

The predefined accounts are intended for:
- initial setup
- demo or internal usage

For production environment:
- passwords must be changed
- system should support secure password management
- default credentials must not be reused

---

## 6. Future Enhancement (Optional)

- Allow creating multiple users
- Allow password change
- Integrate with SSO (e.g. O365)
- Role-based data visibility (Admin sees full data, User sees masked data)
