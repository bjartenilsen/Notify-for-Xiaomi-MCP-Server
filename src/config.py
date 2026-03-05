"""
Configuration module for Notify Xiaomi MCP Server.

This module defines file paths and constants used throughout the server.
All configuration files are stored in ~/.notify-xiaomi-mcp/
"""

from pathlib import Path

# Configuration directory in user's home folder
CONFIG_DIR = Path.home() / ".notify-xiaomi-mcp"
CONFIG_DIR.mkdir(exist_ok=True)

# File paths for Google Drive authentication and database
CREDENTIALS_PATH = CONFIG_DIR / "credentials.json"
TOKEN_PATH = CONFIG_DIR / "token.pickle"
DATABASE_PATH = CONFIG_DIR / "backup.db"

# Google Drive configuration
DRIVE_FOLDER_NAME = "Notify for xiaomi"
DRIVE_FILE_NAME = "backup.db"

# Query limits
DEFAULT_LIMIT = 100
MAX_LIMIT = 1000
