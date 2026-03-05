# Requirements Document

## Introduction

This document specifies requirements for a local MCP (Model Context Protocol) server that provides health data from the Notify for Xiaomi app. The server downloads a SQLite backup database from Google Drive and exposes health metrics (sleep, heart rate, activity) as MCP tools accessible in Claude Desktop on Windows.

## Glossary

- **MCP_Server**: The Python-based Model Context Protocol server that exposes health data tools
- **Backup_Database**: The SQLite database file (backup.db) exported from Notify for Xiaomi app
- **Google_Drive_Client**: The component that authenticates and downloads files from Google Drive
- **Health_Data_Tool**: An MCP tool that queries and returns health metrics from the Backup_Database
- **OAuth2_Token**: The authentication token stored locally to maintain Google Drive access
- **Query_Validator**: The component that ensures only SELECT statements are executed against the database
- **Timestamp_Converter**: The component that converts Unix timestamps to human-readable date strings

## Requirements

### Requirement 1: Google Drive Authentication

**User Story:** As a user, I want the MCP_Server to authenticate with Google Drive using OAuth2, so that it can access my backup files securely.

#### Acceptance Criteria

1. WHEN the MCP_Server starts for the first time, THE Google_Drive_Client SHALL initiate OAuth2 authentication using credentials.json
2. WHEN OAuth2 authentication succeeds, THE Google_Drive_Client SHALL store the OAuth2_Token in token.pickle
3. WHEN the MCP_Server starts with an existing token.pickle, THE Google_Drive_Client SHALL reuse the OAuth2_Token without prompting for authentication
4. IF the OAuth2_Token is expired, THEN THE Google_Drive_Client SHALL refresh the token automatically
5. IF authentication fails, THEN THE Google_Drive_Client SHALL return an error message in Norwegian describing the failure

### Requirement 2: Database Synchronization

**User Story:** As a user, I want to download the latest backup database from Google Drive, so that I can query current health data.

#### Acceptance Criteria

1. WHEN the nxk_sync_database tool is invoked, THE MCP_Server SHALL locate the folder named "Notify for xiaomi" in Google Drive
2. WHEN the folder is found, THE MCP_Server SHALL download the file named "backup.db" to a local temporary directory
3. IF the Backup_Database already exists locally, THEN THE MCP_Server SHALL overwrite it with the downloaded version
4. IF the folder or file is not found, THEN THE MCP_Server SHALL return an error message in Norwegian indicating what is missing
5. WHEN the download completes successfully, THE MCP_Server SHALL return a confirmation message with the file size and download timestamp

### Requirement 3: Database Schema Inspection

**User Story:** As a user, I want to list all tables in the database with their structure, so that I understand what data is available.

#### Acceptance Criteria

1. WHEN the nxk_list_tables tool is invoked, THE MCP_Server SHALL query the Backup_Database for all table names
2. FOR EACH table, THE MCP_Server SHALL retrieve the column names and data types
3. FOR EACH table, THE MCP_Server SHALL count the total number of rows
4. THE MCP_Server SHALL return the results as JSON containing table name, columns, and row count
5. IF the Backup_Database is not available locally, THEN THE MCP_Server SHALL return an error message in Norwegian prompting to run nxk_sync_database first

### Requirement 4: Sleep Data Retrieval

**User Story:** As a user, I want to retrieve sleep data with readable timestamps, so that I can analyze my sleep patterns.

#### Acceptance Criteria

1. WHEN the nxk_get_sleep tool is invoked, THE MCP_Server SHALL query sleep data from the Backup_Database
2. FOR EACH sleep record, THE Timestamp_Converter SHALL convert Unix timestamps to YYYY-MM-DD HH:MM format
3. WHERE a start_date parameter is provided, THE MCP_Server SHALL filter results to records on or after that date
4. WHERE an end_date parameter is provided, THE MCP_Server SHALL filter results to records on or before that date
5. WHERE a limit parameter is provided, THE MCP_Server SHALL return at most that many records
6. IF no limit is specified, THEN THE MCP_Server SHALL default to 100 records
7. IF the limit exceeds 1000, THEN THE MCP_Server SHALL return at most 1000 records
8. THE MCP_Server SHALL return the results as JSON with readable timestamps

### Requirement 5: Heart Rate Data Retrieval

**User Story:** As a user, I want to retrieve heart rate measurements with readable timestamps, so that I can track my cardiovascular health.

#### Acceptance Criteria

1. WHEN the nxk_get_heart_rate tool is invoked, THE MCP_Server SHALL query heart rate data from the Backup_Database
2. FOR EACH heart rate record, THE Timestamp_Converter SHALL convert Unix timestamps to YYYY-MM-DD HH:MM format
3. WHERE a start_date parameter is provided, THE MCP_Server SHALL filter results to records on or after that date
4. WHERE an end_date parameter is provided, THE MCP_Server SHALL filter results to records on or before that date
5. WHERE a limit parameter is provided, THE MCP_Server SHALL return at most that many records
6. IF no limit is specified, THEN THE MCP_Server SHALL default to 100 records
7. IF the limit exceeds 1000, THEN THE MCP_Server SHALL return at most 1000 records
8. THE MCP_Server SHALL return the results as JSON with BPM values and readable timestamps

### Requirement 6: Activity Data Retrieval

**User Story:** As a user, I want to retrieve activity data including steps, calories, and distance, so that I can monitor my daily physical activity.

#### Acceptance Criteria

1. WHEN the nxk_get_activity tool is invoked, THE MCP_Server SHALL query activity data from the Backup_Database
2. FOR EACH activity record, THE Timestamp_Converter SHALL convert Unix timestamps to YYYY-MM-DD HH:MM format
3. THE MCP_Server SHALL include steps, calories, and distance in the results
4. WHERE a start_date parameter is provided, THE MCP_Server SHALL filter results to records on or after that date
5. WHERE an end_date parameter is provided, THE MCP_Server SHALL filter results to records on or before that date
6. WHERE a limit parameter is provided, THE MCP_Server SHALL return at most that many records
7. IF no limit is specified, THEN THE MCP_Server SHALL default to 100 records
8. IF the limit exceeds 1000, THEN THE MCP_Server SHALL return at most 1000 records
9. THE MCP_Server SHALL return the results as JSON with readable timestamps

### Requirement 7: Custom Query Execution

**User Story:** As a user, I want to execute custom SQL queries against the database, so that I can explore data beyond the predefined tools.

#### Acceptance Criteria

1. WHEN the nxk_query tool is invoked with a SQL query, THE Query_Validator SHALL verify the query contains only SELECT statements
2. IF the query contains INSERT, UPDATE, DELETE, DROP, ALTER, or CREATE statements, THEN THE Query_Validator SHALL reject the query with an error message in Norwegian
3. WHEN a valid SELECT query is provided, THE MCP_Server SHALL execute it against the Backup_Database
4. THE MCP_Server SHALL return the query results as JSON
5. IF the query execution fails, THEN THE MCP_Server SHALL return the SQL error message in Norwegian

### Requirement 8: Timestamp Conversion

**User Story:** As a user, I want all timestamps to be in readable format, so that I can easily understand when measurements were taken.

#### Acceptance Criteria

1. WHEN processing any health data record, THE Timestamp_Converter SHALL detect whether timestamps are in milliseconds or seconds
2. THE Timestamp_Converter SHALL convert Unix timestamps in milliseconds by dividing by 1000
3. THE Timestamp_Converter SHALL convert Unix timestamps in seconds directly
4. THE Timestamp_Converter SHALL format all timestamps as YYYY-MM-DD HH:MM in local timezone
5. IF a timestamp cannot be converted, THEN THE Timestamp_Converter SHALL return the original value as a string

### Requirement 9: Read-Only Database Access

**User Story:** As a user, I want the database to remain unmodified, so that my backup data stays intact.

#### Acceptance Criteria

1. THE MCP_Server SHALL open the Backup_Database in read-only mode
2. THE Query_Validator SHALL reject any non-SELECT SQL statements
3. THE MCP_Server SHALL prevent any write operations to the Backup_Database
4. IF a write operation is attempted, THEN THE MCP_Server SHALL return an error message in Norwegian

### Requirement 10: MCP Server Transport

**User Story:** As a user, I want the server to communicate via stdio, so that it integrates with Claude Desktop on Windows.

#### Acceptance Criteria

1. THE MCP_Server SHALL use stdio transport for communication
2. THE MCP_Server SHALL accept MCP protocol messages on standard input
3. THE MCP_Server SHALL send MCP protocol responses to standard output
4. THE MCP_Server SHALL log errors to standard error
5. WHEN invoked from Claude Desktop, THE MCP_Server SHALL start without requiring additional configuration beyond the command path

### Requirement 11: Input Validation

**User Story:** As a developer, I want all tool inputs to be validated, so that the server handles invalid data gracefully.

#### Acceptance Criteria

1. WHERE a date parameter is provided, THE MCP_Server SHALL validate it matches YYYY-MM-DD format
2. WHERE a limit parameter is provided, THE MCP_Server SHALL validate it is a positive integer
3. IF validation fails, THEN THE MCP_Server SHALL return a descriptive error message in Norwegian
4. THE MCP_Server SHALL use Pydantic v2 for input validation
5. THE MCP_Server SHALL reject requests with missing required parameters

### Requirement 12: Error Handling

**User Story:** As a user, I want clear error messages in Norwegian, so that I can understand and fix problems quickly.

#### Acceptance Criteria

1. WHEN any operation fails, THE MCP_Server SHALL return an error message in Norwegian
2. THE error message SHALL describe what went wrong and suggest corrective action where applicable
3. IF the Backup_Database file is missing, THEN THE error message SHALL instruct the user to run nxk_sync_database
4. IF Google Drive authentication fails, THEN THE error message SHALL explain the authentication issue
5. IF a SQL query is invalid, THEN THE error message SHALL include the SQL error details
