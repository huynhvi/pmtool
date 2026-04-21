## 13. Login UI Requirement

### 13.1 Objective
Provide a simple, clean, and professional login interface for both Admin and User roles.

The login screen must:
- be easy to use
- have minimal fields
- ensure secure access to the system

---

### 13.2 Login Screen Structure

The login screen must include:

#### 1. Input Fields
- Account (username or email)
- Password

Both fields are required.

#### 2. Login Button
- A primary button labeled: "Login"
- Clicking the button will trigger authentication

---

### 13.3 Field Behavior

#### Account Field
- Accept text input (username or email)
- Must not be empty

#### Password Field
- Input must be masked (hidden characters)
- Must not be empty

---

### 13.4 Validation

When user clicks "Login":

- If any field is empty:
  → show error message:
  "Account and Password are required"

- If login fails:
  → show error message:
  "Invalid account or password"

---

### 13.5 UI Design

The login UI must:
- be centered on screen
- use a clean and minimal layout
- include:
  - system title or logo (optional)
  - login form card

---

### 13.6 Security Requirement

- Password must not be visible when typing
- No sensitive information displayed on screen
- Do not reveal whether account exists or not

---

### 13.7 User Experience

- Users should be able to login within a few seconds
- No unnecessary steps or fields
- Clear and readable interface

---

### 13.8 Optional Enhancements (Future)

- "Show/Hide Password" toggle
- "Remember Me" checkbox
- "Forgot Password" link
