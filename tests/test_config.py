"""
Unit tests for configuration module.
"""

import pytest
from pathlib import Path
from src.config import (
    CONFIG_DIR,
    CREDENTIALS_PATH,
    TOKEN_PATH,
    DATABASE_PATH,
    DRIVE_FOLDER_NAME,
    DRIVE_FILE_NAME,
    DEFAULT_LIMIT,
    MAX_LIMIT,
)


def test_config_dir_is_in_home():
    """Test that CONFIG_DIR is in user's home directory"""
    assert CONFIG_DIR.parent == Path.home()
    assert CONFIG_DIR.name == ".notify-xiaomi-mcp"


def test_config_dir_exists():
    """Test that CONFIG_DIR is created"""
    assert CONFIG_DIR.exists()
    assert CONFIG_DIR.is_dir()


def test_credentials_path():
    """Test that CREDENTIALS_PATH points to correct location"""
    assert CREDENTIALS_PATH == CONFIG_DIR / "credentials.json"
    assert CREDENTIALS_PATH.parent == CONFIG_DIR


def test_token_path():
    """Test that TOKEN_PATH points to correct location"""
    assert TOKEN_PATH == CONFIG_DIR / "token.pickle"
    assert TOKEN_PATH.parent == CONFIG_DIR


def test_database_path():
    """Test that DATABASE_PATH points to correct location"""
    assert DATABASE_PATH == CONFIG_DIR / "backup.db"
    assert DATABASE_PATH.parent == CONFIG_DIR


def test_drive_folder_name():
    """Test that DRIVE_FOLDER_NAME is correct"""
    assert DRIVE_FOLDER_NAME == "Notify for xiaomi"


def test_drive_file_name():
    """Test that DRIVE_FILE_NAME is correct"""
    assert DRIVE_FILE_NAME == "backup.db"


def test_default_limit():
    """Test that DEFAULT_LIMIT is 100 (Requirements 4.6, 5.6, 6.7)"""
    assert DEFAULT_LIMIT == 100


def test_max_limit():
    """Test that MAX_LIMIT is 1000 (Requirements 4.7, 5.7, 6.8)"""
    assert MAX_LIMIT == 1000


def test_limit_relationship():
    """Test that DEFAULT_LIMIT is less than MAX_LIMIT"""
    assert DEFAULT_LIMIT < MAX_LIMIT
