# Implementation Plan: Notify Xiaomi MCP Server

## Overview

This plan implements a Python-based MCP server that provides health data from the Notify for Xiaomi app. The server downloads a SQLite backup database from Google Drive and exposes six MCP tools for querying sleep, heart rate, and activity data through Claude Desktop on Windows.

## Tasks

- [x] 1. Set up project structure and dependencies
  - Create project directory structure with src/ and tests/ folders
  - Create pyproject.toml with dependencies: fastmcp, google-api-python-client, google-auth-oauthlib, pydantic>=2.0, hypothesis, pytest
  - Create .gitignore for Python project (exclude token.pickle, credentials.json, backup.db)
  - Create README.md with setup instructions
  - _Requirements: 10.1, 11.4_

- [x] 2. Implement configuration and file path management
  - Create config module with paths for credentials.json, token.pickle, and backup.db in ~/.notify-xiaomi-mcp/
  - Define constants for Google Drive folder name ("Notify for xiaomi") and file name ("backup.db")
  - Define query limits (DEFAULT_LIMIT=100, MAX_LIMIT=1000)
  - _Requirements: 4.6, 4.7, 5.6, 5.7, 6.7, 6.8_

- [x] 3. Implement timestamp conversion utilities
  - [x] 3.1 Create TimestampConverter class with convert() method
    - Implement detection for milliseconds vs seconds (threshold: 10 billion)
    - Convert Unix timestamps to datetime objects
    - Format as YYYY-MM-DD HH:MM in local timezone
    - Handle conversion errors by returning original value as string
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5_
  
  - [ ]* 3.2 Write property test for timestamp conversion
    - **Property 11: Timestamp Format Conversion**
    - **Property 12: Timestamp Format Detection**
    - **Validates: Requirements 8.4, 8.1, 8.2**

- [x] 4. Implement query validation
  - [x] 4.1 Create QueryValidator class with is_select_only() method
    - Remove SQL comments (-- and /* */)
    - Normalize whitespace and convert to uppercase
    - Check for forbidden keywords: INSERT, UPDATE, DELETE, DROP, ALTER, CREATE, TRUNCATE, REPLACE, PRAGMA
    - Verify query starts with SELECT
    - Return Norwegian error messages for invalid queries
    - _Requirements: 7.1, 7.2, 9.2_
  
  - [ ]* 4.2 Write property test for query validation
    - **Property 14: Query Validation (SELECT-Only)**
    - **Validates: Requirements 7.1, 7.2, 9.2**

- [x] 5. Implement Pydantic models for input validation
  - [x] 5.1 Create DateRangeParams base model
    - Add start_date, end_date (Optional[str]) and limit (Optional[int]) fields
    - Add field_validator for date format (YYYY-MM-DD)
    - Add field_validator for limit (1 <= limit <= 1000)
    - Use Norwegian error messages in validators
    - _Requirements: 11.1, 11.2, 11.3, 11.4_
  
  - [x] 5.2 Create SleepParams, HeartRateParams, ActivityParams models
    - Inherit from DateRangeParams
    - _Requirements: 4.3, 4.4, 4.5, 5.3, 5.4, 5.5, 6.4, 6.5, 6.6_
  
  - [x] 5.3 Create QueryParams model
    - Add sql field with min_length=1
    - Add field_validator that uses QueryValidator.is_select_only()
    - _Requirements: 7.1, 7.2_
  
  - [ ]* 5.4 Write property tests for input validation
    - **Property 17: Date Format Validation**
    - **Property 18: Limit Parameter Validation**
    - **Property 19: Required Parameter Validation**
    - **Validates: Requirements 11.1, 11.2, 11.5**

- [x] 6. Implement Google Drive client
  - [x] 6.1 Create GoogleDriveClient class with authentication
    - Implement authenticate() method using OAuth2 flow
    - Load existing token from token.pickle if available
    - Refresh expired tokens automatically
    - Save new tokens to token.pickle
    - Use SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
    - Return Norwegian error messages for authentication failures
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_
  
  - [x] 6.2 Implement find_folder() method
    - Search Google Drive for folder by name
    - Return folder ID or None
    - _Requirements: 2.1_
  
  - [x] 6.3 Implement download_file() method
    - Download file from specified folder to destination path
    - Overwrite existing file if present
    - Return success status and file size
    - Return Norwegian error messages for failures
    - _Requirements: 2.2, 2.3, 2.4_
  
  - [ ]* 6.4 Write property tests for Google Drive client
    - **Property 1: OAuth2 Token Persistence**
    - **Property 2: OAuth2 Token Refresh**
    - **Property 3: Google Drive Folder Location**
    - **Property 4: Database File Download**
    - **Property 5: Database File Overwrite**
    - **Validates: Requirements 1.2, 1.3, 1.4, 2.1, 2.2, 2.3**

- [x] 7. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 8. Implement database manager
  - [x] 8.1 Create DatabaseManager class with read-only connection
    - Implement get_readonly_connection() using URI with ?mode=ro
    - Set row_factory to sqlite3.Row for dict-like access
    - _Requirements: 9.1, 9.3_
  
  - [x] 8.2 Implement exists() method
    - Check if database file exists at configured path
    - _Requirements: 3.5_
  
  - [x] 8.3 Implement get_tables() method
    - Query sqlite_master for all table names
    - For each table, get column names and types from PRAGMA table_info
    - For each table, count total rows
    - Return list of dicts with name, columns, and row_count
    - _Requirements: 3.1, 3.2, 3.3, 3.4_
  
  - [x] 8.4 Implement execute_query() method
    - Execute SELECT query with optional parameters
    - Return results as list of dicts
    - Handle SQLite errors with Norwegian messages
    - _Requirements: 7.3, 7.4, 7.5_
  
  - [x] 8.5 Implement get_sleep_data() method
    - Build SELECT query with date range filters
    - Apply limit (default 100, max 1000)
    - Convert timestamp fields using TimestampConverter
    - Return list of sleep records with readable timestamps
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7, 4.8_
  
  - [x] 8.6 Implement get_heart_rate_data() method
    - Build SELECT query with date range filters
    - Apply limit (default 100, max 1000)
    - Convert timestamp fields using TimestampConverter
    - Return list of heart rate records with BPM and readable timestamps
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7, 5.8_
  
  - [x] 8.7 Implement get_activity_data() method
    - Build SELECT query with date range filters
    - Apply limit (default 100, max 1000)
    - Convert timestamp fields using TimestampConverter
    - Include steps, calories, and distance fields
    - Return list of activity records with readable timestamps
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7, 6.8, 6.9_
  
  - [ ]* 8.8 Write property tests for database manager
    - **Property 7: Table Schema Completeness**
    - **Property 8: Health Data Date Filtering (Start Date)**
    - **Property 9: Health Data Date Filtering (End Date)**
    - **Property 10: Health Data Limit Enforcement**
    - **Property 13: Activity Data Field Completeness**
    - **Property 15: Valid SELECT Query Execution**
    - **Property 16: Read-Only Database Connection**
    - **Validates: Requirements 3.1-3.4, 4.3-4.7, 5.3-5.7, 6.3-6.8, 7.3, 7.4, 9.1, 9.3**

- [x] 9. Implement FastMCP server and tools
  - [x] 9.1 Create FastMCP server instance
    - Initialize FastMCP with name "Notify Xiaomi Health Data"
    - Configure stdio transport
    - Set up error logging to stderr
    - _Requirements: 10.1, 10.2, 10.3, 10.4_
  
  - [x] 9.2 Implement nxk_sync_database tool
    - Authenticate with Google Drive using GoogleDriveClient
    - Find "Notify for xiaomi" folder
    - Download backup.db file
    - Return success response with file_size_bytes and download_timestamp
    - Return Norwegian error messages for failures
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_
  
  - [x] 9.3 Implement nxk_list_tables tool
    - Check if database exists, return Norwegian error if not
    - Call DatabaseManager.get_tables()
    - Return JSON with tables, columns, and row counts
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_
  
  - [x] 9.4 Implement nxk_get_sleep tool
    - Validate input using SleepParams model
    - Check if database exists, return Norwegian error if not
    - Call DatabaseManager.get_sleep_data()
    - Return JSON with records and count
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7, 4.8_
  
  - [x] 9.5 Implement nxk_get_heart_rate tool
    - Validate input using HeartRateParams model
    - Check if database exists, return Norwegian error if not
    - Call DatabaseManager.get_heart_rate_data()
    - Return JSON with records and count
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7, 5.8_
  
  - [x] 9.6 Implement nxk_get_activity tool
    - Validate input using ActivityParams model
    - Check if database exists, return Norwegian error if not
    - Call DatabaseManager.get_activity_data()
    - Return JSON with records and count
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7, 6.8, 6.9_
  
  - [x] 9.7 Implement nxk_query tool
    - Validate input using QueryParams model (includes query validation)
    - Check if database exists, return Norwegian error if not
    - Call DatabaseManager.execute_query()
    - Return JSON with columns, rows, and row_count
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_
  
  - [ ]* 9.8 Write property tests for MCP tools
    - **Property 6: Sync Success Response Completeness**
    - **Property 20: Norwegian Error Messages**
    - **Property 21: Error Logging to Stderr**
    - **Validates: Requirements 2.5, 1.5, 2.4, 7.5, 9.4, 11.3, 12.1-12.5, 10.4**

- [x] 10. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 11. Create error handling and Norwegian message catalog
  - Create ERROR_MESSAGES dictionary with all Norwegian error messages
  - Implement get_error_message() helper function
  - Add error response structure with success, error, error_type, and details fields
  - Ensure all error paths use Norwegian messages
  - _Requirements: 1.5, 2.4, 7.5, 9.4, 11.3, 12.1, 12.2, 12.3, 12.4, 12.5_

- [ ]* 12. Write unit tests for edge cases
  - Test default limit is 100 (Requirements 4.6, 5.6, 6.7)
  - Test limit > 1000 is capped at 1000 (Requirements 4.7, 5.7, 6.8)
  - Test missing database error mentions nxk_sync_database (Requirements 3.5, 12.3)
  - Test invalid timestamp returns original as string (Requirements 8.5)
  - Test first-time OAuth2 authentication flow (Requirements 1.1)
  - Test database file overwrite on sync (Requirements 2.3)

- [ ]* 13. Write integration tests
  - Test stdio transport communication (Requirements 10.1, 10.2, 10.3)
  - Test end-to-end execution of all six tools with mock database
  - Test error logging to stderr (Requirements 10.4)
  - Test Claude Desktop integration configuration

- [x] 14. Create Claude Desktop configuration
  - Create example configuration for Claude Desktop on Windows
  - Document how to add server to claude_desktop_config.json
  - Include command path and stdio transport configuration
  - _Requirements: 10.5_

- [x] 15. Create documentation
  - Document setup process (installing dependencies, obtaining credentials.json)
  - Document OAuth2 authentication flow for first-time users
  - Document all six MCP tools with examples
  - Document error messages and troubleshooting
  - Create example queries for nxk_query tool
  - _Requirements: All_

- [x] 16. Final checkpoint - Ensure all tests pass
  - Run full test suite with pytest
  - Verify property-based tests pass with 100+ examples each
  - Check test coverage meets goals (85% line, 80% branch, 100% property)
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation at key milestones
- Property tests validate universal correctness properties (21 total)
- Unit tests validate specific examples and edge cases
- All error messages must be in Norwegian per requirements
- Database access is strictly read-only throughout implementation
