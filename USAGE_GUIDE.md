# Notify Xiaomi MCP Server - Usage Guide

This guide provides comprehensive documentation for using the Notify Xiaomi MCP Server, including detailed tool descriptions, examples, and troubleshooting.

## Table of Contents

1. [Getting Started](#getting-started)
2. [OAuth2 Authentication Flow](#oauth2-authentication-flow)
3. [MCP Tools Reference](#mcp-tools-reference)
4. [Example Queries](#example-queries)
5. [Error Messages and Troubleshooting](#error-messages-and-troubleshooting)
6. [Advanced Usage](#advanced-usage)

## Getting Started

### Prerequisites

Before using the MCP server, ensure you have:

1. ✅ Completed installation (see [README.md](README.md))
2. ✅ Obtained Google Drive API credentials
3. ✅ Configured Claude Desktop (see [CLAUDE_DESKTOP_SETUP.md](CLAUDE_DESKTOP_SETUP.md))
4. ✅ Notify for Xiaomi app backing up to Google Drive

### First-Time Setup Workflow

1. **Sync Database**: Run `nxk_sync_database` to authenticate and download your data
2. **Explore Schema**: Run `nxk_list_tables` to see available data
3. **Query Data**: Use specific tools or custom queries to access your health metrics

## OAuth2 Authentication Flow

### First-Time Authentication

When you run `nxk_sync_database` for the first time:

1. **Browser Opens**: A browser window will open automatically
2. **Google Sign-In**: Sign in with your Google account
3. **Permission Request**: Google will ask for permission to access your Drive (read-only)
4. **Grant Access**: Click "Allow" to grant permission
5. **Token Saved**: The authentication token is saved to `~/.notify-xiaomi-mcp/token.pickle`
6. **Download Begins**: The backup.db file is downloaded automatically

### Subsequent Uses

After first-time authentication:

- The server automatically reuses the saved token
- No browser window opens
- Authentication is seamless and instant
- Token is automatically refreshed when expired

### Token Management

**Token Location**: `~/.notify-xiaomi-mcp/token.pickle`

**Token Refresh**: Tokens expire after a period of time. The server automatically refreshes expired tokens using the refresh token.

**Re-authentication**: If you need to re-authenticate (e.g., after revoking access):
1. Delete `~/.notify-xiaomi-mcp/token.pickle`
2. Run `nxk_sync_database` again
3. Complete the OAuth2 flow again

### Security Notes

- The server requests **read-only** access to Google Drive
- Tokens are stored locally on your machine
- No credentials are sent to third parties
- The server cannot modify or delete your Google Drive files

## MCP Tools Reference

### 1. nxk_sync_database

**Purpose**: Download the latest backup database from Google Drive

**Parameters**: None

**Returns**:
```json
{
  "success": true,
  "message": "Database synkronisert vellykket",
  "file_size_bytes": 1048576,
  "download_timestamp": "2024-01-15 14:30"
}
```

**Usage in Claude Desktop**:
```
Please sync my health database from Google Drive using nxk_sync_database.
```

**When to Use**:
- First time using the server
- When you want to get the latest data from your phone
- After the Notify app has created a new backup

**Notes**:
- Overwrites any existing local database
- Requires OAuth2 authentication on first run
- The backup must exist in a folder named "Notify for xiaomi" in your Google Drive

---

### 2. nxk_list_tables

**Purpose**: List all tables in the database with their structure and row counts

**Parameters**: None

**Returns**:
```json
{
  "tables": [
    {
      "name": "SLEEP_TABLE",
      "columns": [
        {"name": "id", "type": "INTEGER"},
        {"name": "start", "type": "INTEGER"},
        {"name": "stop", "type": "INTEGER"},
        {"name": "deep", "type": "INTEGER"},
        {"name": "light", "type": "INTEGER"}
      ],
      "row_count": 365
    },
    {
      "name": "HEART_RATE_TABLE",
      "columns": [
        {"name": "id", "type": "INTEGER"},
        {"name": "date", "type": "INTEGER"},
        {"name": "heart_rate", "type": "INTEGER"}
      ],
      "row_count": 8760
    }
  ]
}
```

**Usage in Claude Desktop**:
```
Show me all the tables in my health database using nxk_list_tables.
```

**When to Use**:
- Exploring the database structure
- Finding table names for custom queries
- Understanding what data is available
- Checking how much data you have

**Notes**:
- Requires database to be synced first
- Shows actual column names from the SQLite database
- Row counts reflect current database state

---

### 3. nxk_get_sleep

**Purpose**: Retrieve sleep data with human-readable timestamps

**Parameters**:
- `start_date` (optional): Start date in YYYY-MM-DD format
- `end_date` (optional): End date in YYYY-MM-DD format
- `limit` (optional): Maximum number of records (default: 100, max: 1000)

**Returns**:
```json
{
  "records": [
    {
      "id": 1,
      "start_time": "2024-01-15 23:30",
      "end_time": "2024-01-16 07:15",
      "duration_minutes": 465,
      "deep_sleep_minutes": 120,
      "light_sleep_minutes": 345
    }
  ],
  "count": 1
}
```

**Usage Examples**:

**Get last 10 sleep records**:
```
Show me my last 10 sleep records using nxk_get_sleep with limit 10.
```

**Get sleep data for a specific date range**:
```
Get my sleep data from January 1 to January 31, 2024 using nxk_get_sleep with:
- start_date: "2024-01-01"
- end_date: "2024-01-31"
```

**Get all sleep data from a specific date**:
```
Show me all my sleep data since December 1, 2023 using nxk_get_sleep with:
- start_date: "2023-12-01"
- limit: 1000
```

**Notes**:
- Timestamps are converted to YYYY-MM-DD HH:MM format
- Default limit is 100 records
- Maximum limit is 1000 records
- Records are typically ordered by date (depends on database)

---

### 4. nxk_get_heart_rate

**Purpose**: Retrieve heart rate measurements with human-readable timestamps

**Parameters**:
- `start_date` (optional): Start date in YYYY-MM-DD format
- `end_date` (optional): End date in YYYY-MM-DD format
- `limit` (optional): Maximum number of records (default: 100, max: 1000)

**Returns**:
```json
{
  "records": [
    {
      "id": 1,
      "timestamp": "2024-01-15 14:30",
      "bpm": 72
    }
  ],
  "count": 1
}
```

**Usage Examples**:

**Get recent heart rate measurements**:
```
Show me my last 50 heart rate measurements using nxk_get_heart_rate with limit 50.
```

**Get heart rate for a specific day**:
```
Get my heart rate data for January 15, 2024 using nxk_get_heart_rate with:
- start_date: "2024-01-15"
- end_date: "2024-01-15"
```

**Get heart rate trends over a month**:
```
Show me my heart rate data for January 2024 using nxk_get_heart_rate with:
- start_date: "2024-01-01"
- end_date: "2024-01-31"
- limit: 1000
```

**Notes**:
- BPM = Beats Per Minute
- Measurements are taken automatically by the Xiaomi device
- Frequency depends on device settings
- Timestamps show when each measurement was taken

---

### 5. nxk_get_activity

**Purpose**: Retrieve activity data including steps, calories, and distance

**Parameters**:
- `start_date` (optional): Start date in YYYY-MM-DD format
- `end_date` (optional): End date in YYYY-MM-DD format
- `limit` (optional): Maximum number of records (default: 100, max: 1000)

**Returns**:
```json
{
  "records": [
    {
      "id": 1,
      "date": "2024-01-15 00:00",
      "steps": 8543,
      "calories": 342.5,
      "distance_meters": 6234.2
    }
  ],
  "count": 1
}
```

**Usage Examples**:

**Get last 30 days of activity**:
```
Show me my activity data for the last 30 days using nxk_get_activity with limit 30.
```

**Get activity for a specific week**:
```
Get my activity data for the week of January 15-21, 2024 using nxk_get_activity with:
- start_date: "2024-01-15"
- end_date: "2024-01-21"
```

**Get all activity data**:
```
Show me all my activity data using nxk_get_activity with limit 1000.
```

**Notes**:
- Steps: Total steps taken
- Calories: Estimated calories burned
- Distance: Total distance in meters
- Data is typically aggregated per day

---

### 6. nxk_query

**Purpose**: Execute custom SELECT queries against the database

**Parameters**:
- `sql` (required): SQL SELECT statement

**Returns**:
```json
{
  "columns": ["id", "start", "stop", "deep"],
  "rows": [
    [1, 1705359000, 1705386900, 120],
    [2, 1705445400, 1705473300, 135]
  ],
  "row_count": 2
}
```

**Usage Examples**:

See the [Example Queries](#example-queries) section below for detailed examples.

**Security Notes**:
- **Only SELECT queries are allowed**
- INSERT, UPDATE, DELETE, DROP, ALTER, CREATE are blocked
- Database is opened in read-only mode
- Your backup data cannot be modified

**Validation**:
- Query must start with SELECT
- Forbidden keywords are detected and rejected
- SQL comments are removed before validation

---

## Example Queries

This section provides example SQL queries you can use with the `nxk_query` tool.

### Basic Queries

**Get first 5 sleep records**:
```sql
SELECT * FROM SLEEP_TABLE LIMIT 5
```

**Get first 10 heart rate measurements**:
```sql
SELECT * FROM HEART_RATE_TABLE LIMIT 10
```

**Get first 7 activity records**:
```sql
SELECT * FROM ACTIVITY_TABLE LIMIT 7
```

### Filtering Queries

**Get sleep records after a specific timestamp**:
```sql
SELECT * FROM SLEEP_TABLE 
WHERE start > 1704067200 
LIMIT 10
```

**Get heart rate measurements above 100 BPM**:
```sql
SELECT * FROM HEART_RATE_TABLE 
WHERE heart_rate > 100 
LIMIT 50
```

**Get days with more than 10,000 steps**:
```sql
SELECT * FROM ACTIVITY_TABLE 
WHERE steps > 10000 
ORDER BY steps DESC 
LIMIT 20
```

### Aggregation Queries

**Calculate average sleep duration**:
```sql
SELECT AVG(stop - start) / 3600.0 as avg_hours 
FROM SLEEP_TABLE
```

**Calculate average heart rate**:
```sql
SELECT AVG(heart_rate) as avg_bpm 
FROM HEART_RATE_TABLE
```

**Calculate total steps**:
```sql
SELECT SUM(steps) as total_steps 
FROM ACTIVITY_TABLE
```

**Count sleep records by month**:
```sql
SELECT 
  strftime('%Y-%m', datetime(start, 'unixepoch')) as month,
  COUNT(*) as sleep_count
FROM SLEEP_TABLE
GROUP BY month
ORDER BY month DESC
```

### Advanced Queries

**Get sleep quality statistics**:
```sql
SELECT 
  COUNT(*) as total_nights,
  AVG(deep) as avg_deep_minutes,
  AVG(light) as avg_light_minutes,
  AVG(stop - start) / 3600.0 as avg_total_hours
FROM SLEEP_TABLE
```

**Get daily step statistics**:
```sql
SELECT 
  MIN(steps) as min_steps,
  MAX(steps) as max_steps,
  AVG(steps) as avg_steps,
  SUM(steps) as total_steps
FROM ACTIVITY_TABLE
```

**Get heart rate ranges**:
```sql
SELECT 
  MIN(heart_rate) as min_bpm,
  MAX(heart_rate) as max_bpm,
  AVG(heart_rate) as avg_bpm,
  COUNT(*) as measurement_count
FROM HEART_RATE_TABLE
```

**Get best sleep nights (most deep sleep)**:
```sql
SELECT 
  datetime(start, 'unixepoch') as sleep_date,
  deep as deep_minutes,
  (stop - start) / 3600.0 as total_hours
FROM SLEEP_TABLE
ORDER BY deep DESC
LIMIT 10
```

**Get most active days**:
```sql
SELECT 
  datetime(date, 'unixepoch') as activity_date,
  steps,
  calories,
  distance_meters / 1000.0 as distance_km
FROM ACTIVITY_TABLE
ORDER BY steps DESC
LIMIT 10
```

### Date Range Queries

**Get sleep data for a specific month**:
```sql
SELECT * FROM SLEEP_TABLE
WHERE datetime(start, 'unixepoch') BETWEEN '2024-01-01' AND '2024-01-31'
ORDER BY start DESC
```

**Get heart rate for a specific day**:
```sql
SELECT * FROM HEART_RATE_TABLE
WHERE date(datetime(date, 'unixepoch')) = '2024-01-15'
ORDER BY date ASC
```

**Get activity for last 7 days** (assuming recent data):
```sql
SELECT * FROM ACTIVITY_TABLE
ORDER BY date DESC
LIMIT 7
```

### Joining Queries (if applicable)

**Note**: The actual table structure may vary. Use `nxk_list_tables` to see available tables and columns.

If your database has related tables, you can join them:

```sql
SELECT 
  s.start as sleep_start,
  s.deep as deep_sleep,
  a.steps as daily_steps
FROM SLEEP_TABLE s
LEFT JOIN ACTIVITY_TABLE a ON date(datetime(s.start, 'unixepoch')) = date(datetime(a.date, 'unixepoch'))
LIMIT 10
```

### Tips for Writing Queries

1. **Use LIMIT**: Always use LIMIT to avoid returning too much data
2. **Check Table Names**: Use `nxk_list_tables` to see exact table and column names
3. **Timestamp Conversion**: Use `datetime(column, 'unixepoch')` to convert Unix timestamps
4. **Date Formatting**: Use `strftime()` for custom date formats
5. **Test Small**: Start with `LIMIT 5` to test your query before increasing the limit

## Error Messages and Troubleshooting

All error messages are in Norwegian. This section explains each error and how to resolve it.

### Authentication Errors

#### "Fant ikke credentials.json"

**English**: credentials.json not found

**Cause**: The OAuth2 credentials file is missing

**Solution**:
1. Download credentials.json from Google Cloud Console
2. Place it at `~/.notify-xiaomi-mcp/credentials.json`
3. On Windows: `C:\Users\YourUsername\.notify-xiaomi-mcp\credentials.json`

**Steps to obtain credentials.json**:
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create or select a project
3. Enable Google Drive API
4. Create OAuth2 credentials (Desktop application)
5. Download the JSON file
6. Rename it to `credentials.json`

---

#### "Google Drive-autentisering feilet"

**English**: Google Drive authentication failed

**Cause**: OAuth2 authentication failed

**Solutions**:
1. **Delete token and re-authenticate**:
   - Delete `~/.notify-xiaomi-mcp/token.pickle`
   - Run `nxk_sync_database` again
   
2. **Verify credentials.json**:
   - Ensure the file is valid JSON
   - Ensure it contains OAuth2 client credentials
   
3. **Check Google Cloud project**:
   - Verify Drive API is enabled
   - Verify OAuth2 consent screen is configured
   - Verify credentials are for "Desktop application" type

---

#### "Kunne ikke fornye tilgangstokenet"

**English**: Could not refresh access token

**Cause**: Token refresh failed (token may be revoked)

**Solution**:
1. Delete `~/.notify-xiaomi-mcp/token.pickle`
2. Run `nxk_sync_database` to re-authenticate
3. Complete the OAuth2 flow again

---

### Resource Errors

#### "Databasen ble ikke funnet. Kjør nxk_sync_database først"

**English**: Database not found. Run nxk_sync_database first

**Cause**: The backup.db file doesn't exist locally

**Solution**:
1. Run `nxk_sync_database` to download the database
2. Ensure the download completes successfully
3. Verify the file exists at `~/.notify-xiaomi-mcp/backup.db`

---

#### "Fant ikke mappen 'Notify for xiaomi' i Google Drive"

**English**: Folder 'Notify for xiaomi' not found in Google Drive

**Cause**: The backup folder doesn't exist in your Google Drive

**Solutions**:
1. **Configure Notify app to backup to Google Drive**:
   - Open Notify for Xiaomi app
   - Go to Settings
   - Enable "Backup to Google Drive"
   - Wait for initial backup to complete

2. **Check folder name**:
   - Open Google Drive in browser
   - Look for a folder named exactly "Notify for xiaomi"
   - Folder name is case-sensitive

3. **Verify Google account**:
   - Ensure you're authenticating with the same Google account used by the Notify app

---

#### "Fant ikke filen 'backup.db' i mappen"

**English**: File 'backup.db' not found in folder

**Cause**: The backup.db file doesn't exist in the Google Drive folder

**Solutions**:
1. **Trigger a backup in Notify app**:
   - Open Notify for Xiaomi app
   - Go to Settings → Backup
   - Manually trigger a backup
   
2. **Wait for automatic backup**:
   - The app may backup on a schedule
   - Wait for the next automatic backup

3. **Check file name**:
   - Open the "Notify for xiaomi" folder in Google Drive
   - Verify a file named "backup.db" exists

---

#### "Nedlasting av backup.db feilet"

**English**: Download of backup.db failed

**Cause**: File download from Google Drive failed

**Solutions**:
1. Check internet connection
2. Verify Google Drive is accessible
3. Check available disk space
4. Try running `nxk_sync_database` again

---

### Validation Errors

#### "Ugyldig datoformat. Bruk YYYY-MM-DD"

**English**: Invalid date format. Use YYYY-MM-DD

**Cause**: Date parameter is not in the correct format

**Solution**:
- Use format: YYYY-MM-DD (e.g., "2024-01-15")
- Examples:
  - ✅ "2024-01-15"
  - ✅ "2023-12-31"
  - ❌ "15-01-2024"
  - ❌ "01/15/2024"
  - ❌ "2024/01/15"

---

#### "Grenseverdien må være et positivt heltall mellom 1 og 1000"

**English**: Limit must be a positive integer between 1 and 1000

**Cause**: Limit parameter is invalid

**Solution**:
- Use a number between 1 and 1000
- Examples:
  - ✅ 10
  - ✅ 100
  - ✅ 1000
  - ❌ 0
  - ❌ -5
  - ❌ 5000
  - ❌ "ten"

---

#### "Kun SELECT-spørringer er tillatt"

**English**: Only SELECT queries are allowed

**Cause**: SQL query contains forbidden keywords

**Solution**:
- Use only SELECT statements
- Remove any INSERT, UPDATE, DELETE, DROP, ALTER, CREATE, TRUNCATE, REPLACE, or PRAGMA statements
- Examples:
  - ✅ `SELECT * FROM SLEEP_TABLE LIMIT 10`
  - ✅ `SELECT AVG(steps) FROM ACTIVITY_TABLE`
  - ❌ `DELETE FROM SLEEP_TABLE`
  - ❌ `UPDATE ACTIVITY_TABLE SET steps = 0`
  - ❌ `DROP TABLE HEART_RATE_TABLE`

**Why**: The database is read-only to protect your backup data from accidental modification.

---

#### "Spørringen må starte med SELECT"

**English**: Query must start with SELECT

**Cause**: SQL query doesn't start with SELECT keyword

**Solution**:
- Ensure your query starts with SELECT
- Remove any leading comments or whitespace
- Examples:
  - ✅ `SELECT * FROM SLEEP_TABLE`
  - ❌ `EXPLAIN SELECT * FROM SLEEP_TABLE`
  - ❌ `WITH cte AS (...) SELECT ...` (CTEs may not be supported)

---

### Execution Errors

#### "Kunne ikke lese fra databasen"

**English**: Could not read from database

**Cause**: Database file is corrupted or inaccessible

**Solutions**:
1. Re-download the database:
   - Run `nxk_sync_database` to get a fresh copy
2. Check file permissions:
   - Ensure the file at `~/.notify-xiaomi-mcp/backup.db` is readable
3. Check disk space:
   - Ensure sufficient disk space is available

---

#### "SQL-spørring feilet"

**English**: SQL query failed

**Cause**: SQL syntax error or invalid table/column names

**Solutions**:
1. **Check table names**:
   - Run `nxk_list_tables` to see exact table names
   - Table names are case-sensitive
   
2. **Check column names**:
   - Use `nxk_list_tables` to see column names for each table
   - Column names are case-sensitive
   
3. **Verify SQL syntax**:
   - Test your query with a simple version first
   - Add complexity incrementally
   
4. **Check for typos**:
   - Verify spelling of table and column names
   - Check for missing commas or parentheses

---

#### "Kunne ikke konvertere tidsstempel"

**English**: Could not convert timestamp

**Cause**: Timestamp value is invalid or in unexpected format

**Solution**:
- This is usually handled gracefully (original value returned as string)
- If you see this error, the timestamp field may contain unexpected data
- Use `nxk_query` to inspect the raw timestamp values

---

## Advanced Usage

### Working with Timestamps

The database stores timestamps as Unix timestamps (seconds or milliseconds since January 1, 1970).

**Automatic Conversion**: The health data tools (nxk_get_sleep, nxk_get_heart_rate, nxk_get_activity) automatically convert timestamps to YYYY-MM-DD HH:MM format.

**Manual Conversion in Queries**: When using `nxk_query`, you can convert timestamps manually:

```sql
-- Convert Unix timestamp to readable date
SELECT datetime(start, 'unixepoch') as readable_date
FROM SLEEP_TABLE
LIMIT 5
```

```sql
-- Filter by date range
SELECT * FROM SLEEP_TABLE
WHERE datetime(start, 'unixepoch') BETWEEN '2024-01-01' AND '2024-01-31'
```

```sql
-- Extract date parts
SELECT 
  strftime('%Y', datetime(start, 'unixepoch')) as year,
  strftime('%m', datetime(start, 'unixepoch')) as month,
  strftime('%d', datetime(start, 'unixepoch')) as day
FROM SLEEP_TABLE
LIMIT 5
```

### Analyzing Trends

**Weekly averages**:
```sql
SELECT 
  strftime('%Y-W%W', datetime(date, 'unixepoch')) as week,
  AVG(steps) as avg_steps,
  AVG(calories) as avg_calories
FROM ACTIVITY_TABLE
GROUP BY week
ORDER BY week DESC
LIMIT 12
```

**Monthly sleep quality**:
```sql
SELECT 
  strftime('%Y-%m', datetime(start, 'unixepoch')) as month,
  AVG(deep) as avg_deep_sleep,
  AVG((stop - start) / 3600.0) as avg_total_hours,
  COUNT(*) as nights
FROM SLEEP_TABLE
GROUP BY month
ORDER BY month DESC
```

**Heart rate by time of day**:
```sql
SELECT 
  strftime('%H', datetime(date, 'unixepoch')) as hour,
  AVG(heart_rate) as avg_bpm,
  COUNT(*) as measurements
FROM HEART_RATE_TABLE
GROUP BY hour
ORDER BY hour
```

### Exporting Data

To export data for analysis in other tools:

1. **Use nxk_query to get the data**
2. **Ask Claude to format it** (CSV, JSON, etc.)
3. **Copy the formatted data** to your analysis tool

Example:
```
Please use nxk_query to get my sleep data for January 2024, 
then format it as CSV so I can import it into Excel.
```

### Performance Tips

1. **Use LIMIT**: Always limit results to avoid long query times
2. **Index awareness**: The database may have indexes on date/timestamp columns
3. **Avoid SELECT ***: Select only the columns you need
4. **Use aggregation**: Let SQLite do the math instead of processing all rows

### Database Schema Exploration

**Find all tables**:
```
Use nxk_list_tables to show me all available tables.
```

**Inspect a specific table**:
```
Use nxk_query with: SELECT * FROM table_name LIMIT 5
```

**Count records in each table**:
```
Use nxk_list_tables (it shows row counts automatically)
```

### Combining Multiple Queries

You can ask Claude to run multiple queries and combine the results:

```
Please:
1. Get my average sleep duration for January using nxk_query
2. Get my average steps for January using nxk_query
3. Compare them and tell me if there's a correlation
```

### Data Privacy

**Local Storage**: All data is stored locally on your machine:
- Database: `~/.notify-xiaomi-mcp/backup.db`
- Token: `~/.notify-xiaomi-mcp/token.pickle`
- Credentials: `~/.notify-xiaomi-mcp/credentials.json`

**No Cloud Processing**: The MCP server runs entirely on your local machine. Your health data is not sent to any external servers (except Google Drive for the initial download).

**Read-Only Access**: The server cannot modify your backup data. All database operations are read-only.

### Backup and Maintenance

**Backup your data**:
```bash
# Copy the database file
cp ~/.notify-xiaomi-mcp/backup.db ~/my-backups/backup-2024-01-15.db
```

**Update to latest data**:
```
Use nxk_sync_database to download the latest backup from Google Drive.
```

**Check database size**:
```bash
# On Windows (PowerShell)
Get-Item ~/.notify-xiaomi-mcp/backup.db | Select-Object Length

# On Linux/Mac
ls -lh ~/.notify-xiaomi-mcp/backup.db
```

## Support and Resources

### Documentation

- [README.md](README.md) - Installation and quick start
- [CLAUDE_DESKTOP_SETUP.md](CLAUDE_DESKTOP_SETUP.md) - Claude Desktop configuration
- This guide - Comprehensive usage documentation

### External Resources

- [MCP Protocol](https://modelcontextprotocol.io/) - Learn about Model Context Protocol
- [Google Drive API](https://developers.google.com/drive/api) - Google Drive API documentation
- [SQLite Documentation](https://www.sqlite.org/docs.html) - SQLite query reference

### Getting Help

If you encounter issues:

1. Check the [Error Messages and Troubleshooting](#error-messages-and-troubleshooting) section
2. Verify all prerequisites are met
3. Test the server manually from command line
4. Check that your database is synced and accessible

### Contributing

Found an issue or have a suggestion? Contributions are welcome! Please ensure:
- All tests pass
- Code is formatted with Black
- Documentation is updated
- Property-based tests are included for new features

---

**Last Updated**: 2024-01-15
**Version**: 1.0.0
