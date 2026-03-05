# Notify Xiaomi MCP Server

A Python-based Model Context Protocol (MCP) server that provides programmatic access to health data from the Notify for Xiaomi app. The server downloads a SQLite backup database from Google Drive and exposes health metrics through six MCP tools accessible in Claude Desktop on Windows.

## Features

- **Google Drive Integration**: Securely download backup database using OAuth2 authentication
- **Health Data Access**: Query sleep, heart rate, and activity data with readable timestamps
- **Database Inspection**: List all tables and their structure
- **Custom Queries**: Execute custom SELECT queries against the database
- **Read-Only Access**: Ensures backup data remains unmodified
- **Norwegian Error Messages**: Clear, actionable error messages in Norwegian

## MCP Tools

1. **nxk_sync_database**: Download the latest backup database from Google Drive
2. **nxk_list_tables**: List all tables with their structure and row counts
3. **nxk_get_sleep**: Retrieve sleep data with readable timestamps
4. **nxk_get_heart_rate**: Retrieve heart rate measurements
5. **nxk_get_activity**: Retrieve activity data (steps, calories, distance)
6. **nxk_query**: Execute custom SELECT queries

## Requirements

- Python 3.10 or higher
- Google Cloud project with Drive API enabled
- OAuth2 credentials (credentials.json)
- Notify for Xiaomi app with backup to Google Drive

## Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd notify-xiaomi-mcp-server
```

2. Create a virtual environment and install dependencies:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e .
```

3. For development, install with dev dependencies:
```bash
pip install -e ".[dev]"
```

## Setup

### 1. Obtain Google Drive API Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google Drive API
4. Create OAuth2 credentials (Desktop application type)
5. Download the credentials file and save it as `~/.notify-xiaomi-mcp/credentials.json`

### 2. First-Time Authentication

On first run, the server will:
1. Open a browser window for Google OAuth2 authentication
2. Ask you to grant access to your Google Drive (read-only)
3. Save the authentication token to `~/.notify-xiaomi-mcp/token.pickle`

Subsequent runs will reuse the saved token automatically.

### 3. Configure Claude Desktop

Add the server to your Claude Desktop configuration file.

**Quick Setup**:

Edit `%APPDATA%\Claude\claude_desktop_config.json` and add:

```json
{
  "mcpServers": {
    "notify-xiaomi": {
      "command": "python",
      "args": [
        "C:\\path\\to\\notify-xiaomi-mcp-server\\src\\server.py"
      ]
    }
  }
}
```

Replace `C:\\path\\to\\notify-xiaomi-mcp-server` with the actual path to your installation.

**For detailed setup instructions, see [CLAUDE_DESKTOP_SETUP.md](CLAUDE_DESKTOP_SETUP.md)**

**For comprehensive usage documentation, examples, and troubleshooting, see [USAGE_GUIDE.md](USAGE_GUIDE.md)**

## Usage

### Quick Start

1. **Sync Database**: Download the latest backup from Google Drive
   ```
   Use the nxk_sync_database tool in Claude Desktop
   ```

2. **Explore Your Data**: List available tables
   ```
   Use nxk_list_tables (no parameters)
   ```

3. **Query Health Metrics**: Use the specific tools for sleep, heart rate, or activity data

### Example Queries

**Get recent sleep data:**
```
Use nxk_get_sleep with parameters:
- start_date: "2024-01-01"
- limit: 10
```

**Get heart rate measurements:**
```
Use nxk_get_heart_rate with parameters:
- start_date: "2024-01-01"
- end_date: "2024-01-31"
- limit: 100
```

**Get activity data:**
```
Use nxk_get_activity with parameters:
- start_date: "2024-01-01"
- limit: 30
```

**Custom SQL query:**
```
Use nxk_query with parameter:
- sql: "SELECT * FROM SLEEP_TABLE LIMIT 5"
```

### Comprehensive Documentation

For detailed documentation including:
- OAuth2 authentication flow
- Complete tool reference with examples
- 30+ example SQL queries
- Error messages and troubleshooting
- Advanced usage patterns

**See [USAGE_GUIDE.md](USAGE_GUIDE.md)**

## Development

### Running Tests

Run all tests:
```bash
pytest
```

Run with coverage:
```bash
pytest --cov=src --cov-report=html
```

Run property-based tests only:
```bash
pytest -k "property"
```

### Code Formatting

Format code with Black:
```bash
black src/ tests/
```

Lint with Ruff:
```bash
ruff check src/ tests/
```

## Project Structure

```
notify-xiaomi-mcp-server/
├── src/
│   ├── __init__.py
│   ├── server.py              # FastMCP server and tool definitions
│   ├── config.py              # Configuration and file paths
│   ├── google_drive_client.py # Google Drive authentication and download
│   ├── database_manager.py    # Database operations
│   ├── timestamp_converter.py # Timestamp conversion utilities
│   ├── query_validator.py     # SQL query validation
│   └── models.py              # Pydantic models for input validation
├── tests/
│   ├── __init__.py
│   ├── test_timestamp_converter.py
│   ├── test_query_validator.py
│   ├── test_models.py
│   ├── test_google_drive_client.py
│   ├── test_database_manager.py
│   └── test_server.py
├── pyproject.toml
├── .gitignore
└── README.md
```

## Documentation

This project includes comprehensive documentation:

- **[README.md](README.md)** (this file) - Quick start and installation guide
- **[CLAUDE_DESKTOP_SETUP.md](CLAUDE_DESKTOP_SETUP.md)** - Detailed Claude Desktop configuration
- **[USAGE_GUIDE.md](USAGE_GUIDE.md)** - Complete usage guide with examples and troubleshooting
- **[API_REFERENCE.md](API_REFERENCE.md)** - Technical API reference for developers

## Troubleshooting

### Quick Fixes

**Authentication Issues**:
- Ensure credentials.json is in `~/.notify-xiaomi-mcp/credentials.json`
- Delete token.pickle and re-authenticate if needed

**Database Issues**:
- Run `nxk_sync_database` first to download the database
- Ensure Notify app is backing up to Google Drive

**Query Issues**:
- Only SELECT statements are allowed
- Use `nxk_list_tables` to see exact table and column names

### Comprehensive Troubleshooting

For detailed troubleshooting including:
- All error messages explained in English
- Step-by-step solutions
- Common issues and fixes

**See [USAGE_GUIDE.md - Error Messages and Troubleshooting](USAGE_GUIDE.md#error-messages-and-troubleshooting)**

## License

MIT License

## Contributing

Contributions are welcome! Please ensure:
- All tests pass (`pytest`)
- Code is formatted (`black src/ tests/`)
- Coverage remains above 85%
- Property-based tests are included for new features
