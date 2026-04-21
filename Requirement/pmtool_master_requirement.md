# PM Tool Dashboard System – Scope Definition

## 1. System Architecture

The system must be separated into two main layers:

### 1.1 Data Processing Layer (Admin Site)
This layer is responsible for:
- uploading raw data
- parsing and extracting information
- transforming data into standard format
- applying data masking rules
- storing processed data

Only Admin users can access this layer.

### 1.2 Dashboard Layer (User View)
This layer is responsible for:
- reading processed data only
- rendering dashboards
- providing insights to users

Users must NOT have access to raw data.

## 2. Data Source Handling

### 2.1 Raw Data Upload
- Data is uploaded via a separate Admin site
- File format: Excel (.xlsx)

### 2.2 Data Parsing
- System must parse raw data automatically
- Extract required fields for each module

## 3. Data Transformation

After parsing, the system must:
- normalize data format
- standardize values (status, severity, etc.)
- prepare data for dashboard usage

## 4. Data Masking (Mass Rollout Module Only)

### 4.1 Requirement
For Mass Rollout data:
- employee names must be masked before display

### 4.2 Masking Rule
- keep last name (given name) fully visible
- for other parts:
  - keep first letter only
  - format as abbreviation

Example:
- Nguyen Van Anh → N. V. Anh

### 4.3 Usage
- Dashboard must use masked data only
- Raw full name must NOT be displayed
## 5. Dashboard Data Source

The dashboard must:
- read data only from processed dataset
- not directly access raw uploaded files

## 6. Module Scope

### 6.1 Mass Rollout Dashboard
- uses masked employee data
- displays goal setting metrics

### 6.2 Issue Tracking Dashboard
- uses parsed issue data
- does NOT require masking

## 7. Admin Operations

Admin site must support:
- upload file
- trigger data processing
- validate processed data
- manage data versions (optional)

## 8. Security Requirement

- Raw data must not be exposed to end users
- Sensitive information must be masked before display
- Only processed data is accessible to dashboard users

## 9. System Behavior

- Upload → auto process → store → update dashboard
- Dashboard reflects latest processed data
- Data processing must complete before dashboard refresh

## 10. Design Principle

- separate data and presentation clearly
- ensure data privacy
- support scalability for future modules
- maintain simple and clear user experience