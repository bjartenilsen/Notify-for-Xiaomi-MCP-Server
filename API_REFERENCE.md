# API Reference

This document provides technical reference documentation for developers working with or extending the Notify Xiaomi MCP Server.

## Table of Contents

1. [MCP Tools API](#mcp-tools-api)
2. [Python Modules](#python-modules)
3. [Data Models](#data-models)
4. [Error Handling](#error-handling)
5. [Configuration](#configuration)

## MCP Tools API

### Tool Registration

All tools are registered using FastMCP's decorator pattern:

```python
from fastmcp import FastMCP

mcp = FastMCP("Notify Xiaomi Health Data")

@mcp.tool()
def tool_name(param: Type) -> dict:
    """Tool description"""
    # Implementation
```

### nxk_sync_database

**Signature**:
```python
@mcp.tool()
def nxk_sync_database() -> dict
```

**Description**: Downloads the latest backup.db file from Google Drive

**Parameters**: None

**Returns**:
```python
{
    "success": bool,
    "message": str,
    "file_size_bytes": Optional[int],
    "download_timestamp": Optional[str]
}
```

**Errors**:
- Authentication failures
- Folder not found
- File not found
- Download failures

---

### nxk_list_tables

**Signature**:
```python
@mcp.tool()
def nxk_list_tables() -> dict
```

**Description**: Lists all tables in the database with schema and row counts

**Parameters**: None

**Returns**:
```python
{
    "tables": List[{
        "name": str,
        "columns": List[{"name": str, "type": str}],
        "row_count": int
    }]
}
```

**Errors**:
- Database not found
- Database read errors

---

### nxk_get_sleep

**Signature**:
```python
@mcp.tool()
def nxk_get_sleep(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: Optional[int] = 100
) -> dict
```

**Description**: Retrieves sleep data with converted timestamps

**Parameters**:
- `start_date`: Start date filter (YYYY-MM-DD format)
- `end_date`: End date filter (YYYY-MM-DD format)
- `limit`: Maximum records to return (1-1000, default: 100)

**Returns**:
```python
{
    "records": List[Dict[str, Any]],
    "count": int
}
```

**Validation**:
- Date format: YYYY-MM-DD
- Limit range: 1-1000
- Timestamps converted to YYYY-MM-DD HH:MM

**Errors**:
- Invalid date format
- Invalid limit
- Database not found
- Query execution errors

---

### nxk_get_heart_rate

**Signature**:
```python
@mcp.tool()
def nxk_get_heart_rate(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: Optional[int] = 100
) -> dict
```

**Description**: Retrieves heart rate data with converted timestamps

**Parameters**:
- `start_date`: Start date filter (YYYY-MM-DD format)
- `end_date`: End date filter (YYYY-MM-DD format)
- `limit`: Maximum records to return (1-1000, default: 100)

**Returns**:
```python
{
    "records": List[Dict[str, Any]],
    "count": int
}
```

**Validation**:
- Date format: YYYY-MM-DD
- Limit range: 1-1000
- Timestamps converted to YYYY-MM-DD HH:MM

**Errors**:
- Invalid date format
- Invalid limit
- Database not found
- Query execution errors

---

### nxk_get_activity

**Signature**:
```python
@mcp.tool()
def nxk_get_activity(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: Optional[int] = 100
) -> dict
```

**Description**: Retrieves activity data with converted timestamps

**Parameters**:
- `start_date`: Start date filter (YYYY-MM-DD format)
- `end_date`: End date filter (YYYY-MM-DD format)
- `limit`: Maximum records to return (1-1000, default: 100)

**Returns**:
```python
{
    "records": List[Dict[str, Any]],
    "count": int
}
```

**Record Fields**:
- `steps`: Integer
- `calories`: Float
- `distance_meters`: Float
- Additional fields from database

**Validation**:
- Date format: YYYY-MM-DD
- Limit range: 1-1000
- Timestamps converted to YYYY-MM-DD HH:MM

**Errors**:
- Invalid date format
- Invalid limit
- Database not found
- Query execution errors

---

### nxk_query

**Signature**:
```python
@mcp.tool()
def nxk_query(sql: str) -> dict
```

**Description**: Executes custom SELECT queries against the database

**Parameters**:
- `sql`: SQL SELECT statement (required)

**Returns**:
```python
{
    "columns": List[str],
    "rows": List[List[Any]],
    "row_count": int
}
```

**Validation**:
- Must start with SELECT
- Forbidden keywords: INSERT, UPDATE, DELETE, DROP, ALTER, CREATE, TRUNCATE, REPLACE, PRAGMA
- SQL comments are removed before validation

**Errors**:
- Non-SELECT query
- Invalid SQL syntax
- Database not found
- Query execution errors

---

## Python Modules

### config.py

**Purpose**: Configuration and file path management

**Constants**:
```python
CONFIG_DIR: Path              # ~/.notify-xiaomi-mcp/
CREDENTIALS_PATH: Path        # ~/.notify-xiaomi-mcp/credentials.json
TOKEN_PATH: Path              # ~/.notify-xiaomi-mcp/token.pickle
DATABASE_PATH: Path           # ~/.notify-xiaomi-mcp/backup.db

DRIVE_FOLDER_NAME: str        # "Notify for xiaomi"
DRIVE_FILE_NAME: str          # "backup.db"

DEFAULT_LIMIT: int            # 100
MAX_LIMIT: int                # 1000
```

**Functions**:
```python
def ensure_config_dir() -> None:
    """Create config directory if it doesn't exist"""
```

---

### google_drive_client.py

**Purpose**: Google Drive authentication and file operations

**Class**: `GoogleDriveClient`

**Constructor**:
```python
def __init__(self, credentials_path: str, token_path: str):
    """
    Initialize Google Drive client
    
    Args:
        credentials_path: Path to credentials.json
        token_path: Path to token.pickle
    """
```

**Methods**:

```python
def authenticate(self) -> bool:
    """
    Authenticate with Google Drive using OAuth2
    
    Returns:
        True if authentication successful, False otherwise
        
    Side Effects:
        - Opens browser for first-time authentication
        - Saves token to token.pickle
        - Refreshes expired tokens automatically
    """
```

```python
def find_folder(self, folder_name: str) -> Optional[str]:
    """
    Find folder by name in Google Drive
    
    Args:
        folder_name: Name of folder to find
        
    Returns:
        Folder ID if found, None otherwise
    """
```

```python
def download_file(
    self, 
    folder_id: str, 
    filename: str, 
    destination: str
) -> Tuple[bool, Optional[int]]:
    """
    Download file from Google Drive folder
    
    Args:
        folder_id: Google Drive folder ID
        filename: Name of file to download
        destination: Local path to save file
        
    Returns:
        Tuple of (success: bool, file_size: Optional[int])
        
    Side Effects:
        - Overwrites existing file at destination
    """
```

```python
def get_last_error(self) -> str:
    """
    Get last error message in Norwegian
    
    Returns:
        Norwegian error message
    """
```

**OAuth2 Scopes**:
```python
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
```

---

### database_manager.py

**Purpose**: Database operations and queries

**Class**: `DatabaseManager`

**Constructor**:
```python
def __init__(self, db_path: str):
    """
    Initialize database manager
    
    Args:
        db_path: Path to backup.db file
    """
```

**Methods**:

```python
def exists(self) -> bool:
    """
    Check if database file exists
    
    Returns:
        True if database file exists, False otherwise
    """
```

```python
def get_tables(self) -> List[Dict[str, Any]]:
    """
    Get all tables with schema and row counts
    
    Returns:
        List of table info dicts with name, columns, row_count
        
    Raises:
        sqlite3.Error: If database read fails
    """
```

```python
def execute_query(
    self, 
    sql: str, 
    params: Optional[Dict] = None
) -> List[Dict[str, Any]]:
    """
    Execute SELECT query and return results
    
    Args:
        sql: SQL SELECT statement
        params: Optional query parameters
        
    Returns:
        List of result rows as dicts
        
    Raises:
        sqlite3.Error: If query execution fails
    """
```

```python
def get_sleep_data(
    self,
    start_date: Optional[str],
    end_date: Optional[str],
    limit: int
) -> List[Dict[str, Any]]:
    """
    Query sleep data with filters
    
    Args:
        start_date: Start date filter (YYYY-MM-DD)
        end_date: End date filter (YYYY-MM-DD)
        limit: Maximum records (1-1000)
        
    Returns:
        List of sleep records with converted timestamps
    """
```

```python
def get_heart_rate_data(
    self,
    start_date: Optional[str],
    end_date: Optional[str],
    limit: int
) -> List[Dict[str, Any]]:
    """
    Query heart rate data with filters
    
    Args:
        start_date: Start date filter (YYYY-MM-DD)
        end_date: End date filter (YYYY-MM-DD)
        limit: Maximum records (1-1000)
        
    Returns:
        List of heart rate records with converted timestamps
    """
```

```python
def get_activity_data(
    self,
    start_date: Optional[str],
    end_date: Optional[str],
    limit: int
) -> List[Dict[str, Any]]:
    """
    Query activity data with filters
    
    Args:
        start_date: Start date filter (YYYY-MM-DD)
        end_date: End date filter (YYYY-MM-DD)
        limit: Maximum records (1-1000)
        
    Returns:
        List of activity records with converted timestamps
    """
```

**Connection Pattern**:
```python
def _get_readonly_connection(self) -> sqlite3.Connection:
    """
    Open database in read-only mode
    
    Returns:
        SQLite connection with read-only URI
        
    Connection URI: file:{db_path}?mode=ro
    Row Factory: sqlite3.Row (dict-like access)
    """
```

---

### utils.py

**Purpose**: Utility functions for timestamp conversion and query validation

**Timestamp Conversion**:

```python
def convert_timestamp(timestamp: Union[int, float, str]) -> str:
    """
    Convert Unix timestamp to YYYY-MM-DD HH:MM format
    
    Args:
        timestamp: Unix timestamp (seconds or milliseconds)
        
    Returns:
        Formatted timestamp string or original value if conversion fails
        
    Detection:
        - Values > 10,000,000,000 are treated as milliseconds
        - Values <= 10,000,000,000 are treated as seconds
    """
```

```python
def convert_timestamps_in_record(
    record: Dict[str, Any],
    timestamp_fields: List[str]
) -> Dict[str, Any]:
    """
    Convert specified timestamp fields in a record
    
    Args:
        record: Record dict
        timestamp_fields: List of field names to convert
        
    Returns:
        Record with converted timestamp fields
    """
```

**Query Validation**:

```python
def validate_select_query(sql: str) -> Tuple[bool, str]:
    """
    Validate that SQL query is SELECT-only
    
    Args:
        sql: SQL query string
        
    Returns:
        Tuple of (is_valid: bool, error_message: str)
        
    Validation:
        - Removes SQL comments (-- and /* */)
        - Checks for forbidden keywords
        - Ensures query starts with SELECT
        
    Forbidden Keywords:
        INSERT, UPDATE, DELETE, DROP, ALTER, CREATE,
        TRUNCATE, REPLACE, PRAGMA
    """
```

---

### error_handling.py

**Purpose**: Error message catalog and error response formatting

**Constants**:

```python
ERROR_MESSAGES: Dict[str, str] = {
    "auth_no_credentials": "Fant ikke credentials.json...",
    "auth_failed": "Google Drive-autentisering feilet...",
    "db_not_found": "Databasen ble ikke funnet...",
    "folder_not_found": "Fant ikke mappen 'Notify for xiaomi'...",
    "file_not_found": "Fant ikke filen 'backup.db'...",
    "invalid_date_format": "Ugyldig datoformat...",
    "invalid_limit": "Grenseverdien må være...",
    "query_not_select": "Kun SELECT-spørringer er tillatt...",
    # ... more error messages
}
```

**Functions**:

```python
def get_error_message(key: str, **kwargs) -> str:
    """
    Get Norwegian error message with optional formatting
    
    Args:
        key: Error message key
        **kwargs: Format parameters
        
    Returns:
        Formatted Norwegian error message
    """
```

```python
def create_error_response(
    error_type: str,
    message: str,
    details: Optional[str] = None
) -> dict:
    """
    Create standardized error response
    
    Args:
        error_type: Error category (auth, resource, validation, execution)
        message: Norwegian error message
        details: Optional technical details
        
    Returns:
        Error response dict with success=False
    """
```

**Error Categories**:
- `auth`: Authentication errors
- `resource`: Missing files or folders
- `validation`: Input validation errors
- `execution`: Query execution errors

---

### models.py

**Purpose**: Pydantic models for input validation

**Base Model**:

```python
class DateRangeParams(BaseModel):
    """Base model for date range queries"""
    
    start_date: Optional[str] = Field(
        None, 
        description="Start date in YYYY-MM-DD format"
    )
    end_date: Optional[str] = Field(
        None, 
        description="End date in YYYY-MM-DD format"
    )
    limit: Optional[int] = Field(
        100, 
        ge=1, 
        le=1000, 
        description="Maximum number of records"
    )
    
    @field_validator('start_date', 'end_date')
    @classmethod
    def validate_date_format(cls, v: Optional[str]) -> Optional[str]:
        """Validate date format is YYYY-MM-DD"""
        if v is None:
            return v
        try:
            datetime.strptime(v, '%Y-%m-%d')
            return v
        except ValueError:
            raise ValueError('Dato må være i formatet YYYY-MM-DD')
```

**Specific Models**:

```python
class SleepParams(DateRangeParams):
    """Parameters for sleep data queries"""
    pass

class HeartRateParams(DateRangeParams):
    """Parameters for heart rate queries"""
    pass

class ActivityParams(DateRangeParams):
    """Parameters for activity queries"""
    pass
```

**Query Model**:

```python
class QueryParams(BaseModel):
    """Parameters for custom SQL queries"""
    
    sql: str = Field(
        ..., 
        min_length=1, 
        description="SQL SELECT statement"
    )
    
    @field_validator('sql')
    @classmethod
    def validate_select_only(cls, v: str) -> str:
        """Validate query is SELECT-only"""
        is_valid, error = validate_select_query(v)
        if not is_valid:
            raise ValueError(error)
        return v
```

---

## Data Models

### Response Structures

**Success Response**:
```python
{
    "success": True,
    "message": str,
    # ... additional fields
}
```

**Error Response**:
```python
{
    "success": False,
    "error": str,              # Norwegian error message
    "error_type": str,         # auth, resource, validation, execution
    "details": Optional[str]   # Technical details
}
```

**Sync Response**:
```python
{
    "success": bool,
    "message": str,
    "file_size_bytes": Optional[int],
    "download_timestamp": Optional[str]  # YYYY-MM-DD HH:MM
}
```

**Tables Response**:
```python
{
    "tables": [
        {
            "name": str,
            "columns": [
                {"name": str, "type": str}
            ],
            "row_count": int
        }
    ]
}
```

**Health Data Response**:
```python
{
    "records": [
        {
            # Fields vary by data type
            # Timestamps in YYYY-MM-DD HH:MM format
        }
    ],
    "count": int
}
```

**Query Response**:
```python
{
    "columns": List[str],
    "rows": List[List[Any]],
    "row_count": int
}
```

---

## Error Handling

### Error Flow

1. **Exception Occurs**: Operation fails (auth, validation, execution)
2. **Error Captured**: Exception caught in tool function
3. **Error Categorized**: Assigned to error_type (auth, resource, validation, execution)
4. **Message Retrieved**: Norwegian message from ERROR_MESSAGES catalog
5. **Response Created**: Standardized error response dict
6. **Response Returned**: Sent to Claude Desktop via MCP

### Error Categories

**Authentication Errors** (`auth`):
- Missing credentials.json
- OAuth2 authentication failure
- Token refresh failure

**Resource Errors** (`resource`):
- Database file not found
- Google Drive folder not found
- Google Drive file not found
- Download failure

**Validation Errors** (`validation`):
- Invalid date format
- Invalid limit value
- Non-SELECT query
- Missing required parameters

**Execution Errors** (`execution`):
- Database read error
- SQL query execution error
- Timestamp conversion error

### Graceful Degradation

**Timestamp Conversion Failure**:
- Returns original value as string
- Does not fail entire query

**Partial Schema Read**:
- Returns available table information
- Logs errors for failed tables

**Token Refresh Failure**:
- Prompts for re-authentication
- Does not crash server

---

## Configuration

### Environment Variables

The server does not use environment variables by default. All configuration is file-based.

**Optional Environment Variables** (for advanced use):
```bash
# Python unbuffered output (useful for debugging)
PYTHONUNBUFFERED=1

# Log level (if logging is implemented)
LOG_LEVEL=INFO
```

### File Locations

**Configuration Directory**:
```
~/.notify-xiaomi-mcp/
```

On Windows:
```
C:\Users\{Username}\.notify-xiaomi-mcp\
```

**Files**:
- `credentials.json`: OAuth2 credentials (user-provided)
- `token.pickle`: Authentication token (auto-generated)
- `backup.db`: Downloaded database (auto-generated)

### Google Drive Configuration

**Folder Name**: `"Notify for xiaomi"` (case-sensitive)

**File Name**: `"backup.db"` (case-sensitive)

**OAuth2 Scopes**: `['https://www.googleapis.com/auth/drive.readonly']`

### Query Limits

**Default Limit**: 100 records

**Maximum Limit**: 1000 records

**Limit Enforcement**: Applied in database queries

### Database Configuration

**Connection Mode**: Read-only (`?mode=ro`)

**Row Factory**: `sqlite3.Row` (dict-like access)

**Timeout**: Default SQLite timeout (5 seconds)

---

## Extension Points

### Adding New Tools

To add a new MCP tool:

1. **Define Tool Function**:
```python
@mcp.tool()
def nxk_new_tool(param: Type) -> dict:
    """Tool description"""
    # Implementation
    return {"success": True, "data": result}
```

2. **Add Input Validation** (if needed):
```python
class NewToolParams(BaseModel):
    param: Type = Field(..., description="Parameter description")
```

3. **Add Error Messages**:
```python
ERROR_MESSAGES["new_tool_error"] = "Norwegian error message"
```

4. **Add Tests**:
```python
def test_new_tool():
    result = nxk_new_tool(param=value)
    assert result["success"] is True
```

### Adding New Data Sources

To add support for additional data sources:

1. **Identify Table**: Use `nxk_list_tables` to find the table
2. **Create Query Method**: Add method to `DatabaseManager`
3. **Create Tool**: Register new MCP tool
4. **Add Validation**: Create Pydantic model if needed
5. **Add Tests**: Write unit and property tests

### Custom Timestamp Formats

To support different timestamp formats:

1. **Modify `convert_timestamp()`**: Add detection logic
2. **Update Tests**: Add test cases for new format
3. **Document**: Update usage guide

---

## Testing

### Test Structure

```
tests/
├── test_utils.py                  # Timestamp and query validation
├── test_models.py                 # Pydantic model validation
├── test_google_drive_client.py    # Google Drive operations
├── test_database_manager.py       # Database operations
├── test_server.py                 # MCP tools integration
└── test_error_handling.py         # Error handling
```

### Running Tests

```bash
# All tests
pytest

# Specific test file
pytest tests/test_utils.py

# Property-based tests only
pytest -k "property"

# With coverage
pytest --cov=src --cov-report=html
```

### Property-Based Testing

Uses `hypothesis` library for property-based tests:

```python
from hypothesis import given, settings, strategies as st

@settings(max_examples=100)
@given(st.integers(min_value=946684800, max_value=2147483647))
def test_property_timestamp_conversion(timestamp):
    """Test timestamp conversion property"""
    result = convert_timestamp(timestamp)
    assert re.match(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}', result)
```

### Mocking

**Google Drive API**:
```python
from unittest.mock import Mock, patch

@patch('googleapiclient.discovery.build')
def test_google_drive_client(mock_build):
    mock_service = Mock()
    mock_build.return_value = mock_service
    # Test implementation
```

**Database**:
```python
import tempfile
import sqlite3

def test_database_manager():
    with tempfile.NamedTemporaryFile(suffix='.db') as tmp:
        # Create test database
        conn = sqlite3.connect(tmp.name)
        # ... setup test data
        
        # Test DatabaseManager
        manager = DatabaseManager(tmp.name)
        # ... assertions
```

---

## Performance Considerations

### Database Queries

- **Use LIMIT**: Always limit result sets
- **Index Awareness**: Queries on timestamp columns may use indexes
- **Read-Only Mode**: Prevents write locks, improves concurrency

### Google Drive Downloads

- **Token Caching**: Tokens are cached to avoid repeated authentication
- **File Overwrite**: Existing files are overwritten (no versioning)
- **Network Timeout**: Uses default Google API timeout

### Memory Usage

- **Result Sets**: Limited to 1000 records maximum
- **Streaming**: Database results are not streamed (loaded into memory)
- **Token Storage**: Tokens are pickled (small memory footprint)

---

## Security

### Read-Only Database Access

- Database opened with `?mode=ro` URI parameter
- Query validation blocks write operations
- SQLite enforces read-only mode at connection level

### OAuth2 Security

- Uses OAuth2 authorization code flow
- Tokens stored locally (not in cloud)
- Read-only Drive scope requested
- Refresh tokens enable automatic token renewal

### Input Validation

- Pydantic validates all inputs
- SQL injection prevented by query validation
- Date format validation prevents malformed queries

### Error Information Disclosure

- Error messages are user-friendly (Norwegian)
- Technical details included only when helpful
- No sensitive information in error messages

---

## Changelog

### Version 1.0.0 (2024-01-15)

**Initial Release**:
- Six MCP tools for health data access
- Google Drive OAuth2 integration
- Read-only SQLite database access
- Norwegian error messages
- Comprehensive documentation

---

## License

MIT License - See LICENSE file for details

---

**Last Updated**: 2024-01-15
**Version**: 1.0.0
