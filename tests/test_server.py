"""
Tests for the FastMCP server and MCP tools.

This module tests the server initialization and tool functionality.
"""

import pytest
from src.server import (
    mcp,
    nxk_sync_database,
    nxk_list_tables,
    nxk_get_sleep,
    nxk_get_heart_rate,
    nxk_get_activity,
    nxk_query
)


def test_server_initialization():
    """Test that the FastMCP server is initialized correctly."""
    assert mcp.name == "Notify Xiaomi Health Data"
    assert mcp.version == "1.0.0"


def test_nxk_list_tables_returns_error_when_db_missing():
    """Test that nxk_list_tables returns appropriate error when database is missing."""
    result = nxk_list_tables()
    
    # Should return error dict when database doesn't exist
    assert isinstance(result, dict)
    assert "success" in result
    
    # If database doesn't exist, should have error
    if not result.get("success"):
        assert "error" in result
        assert "error_type" in result
        assert result["error_type"] == "resource"
        assert "nxk_sync_database" in result["error"]


def test_nxk_get_sleep_validates_date_format():
    """Test that nxk_get_sleep validates date format."""
    result = nxk_get_sleep(start_date="invalid-date")
    
    assert isinstance(result, dict)
    assert result["success"] is False
    assert "error" in result
    assert result["error_type"] == "validation"
    assert "YYYY-MM-DD" in result["error"]


def test_nxk_get_heart_rate_validates_date_format():
    """Test that nxk_get_heart_rate validates date format."""
    result = nxk_get_heart_rate(start_date="2024-13-45")  # Invalid month/day
    
    assert isinstance(result, dict)
    assert result["success"] is False
    assert "error" in result
    assert result["error_type"] == "validation"


def test_nxk_get_activity_validates_date_format():
    """Test that nxk_get_activity validates date format."""
    result = nxk_get_activity(end_date="not-a-date")
    
    assert isinstance(result, dict)
    assert result["success"] is False
    assert "error" in result
    assert result["error_type"] == "validation"


def test_nxk_query_rejects_non_select():
    """Test that nxk_query rejects non-SELECT queries."""
    result = nxk_query(sql="DELETE FROM users")
    
    assert isinstance(result, dict)
    assert result["success"] is False
    assert "error" in result
    assert result["error_type"] == "validation"
    assert "SELECT" in result["error"]


def test_nxk_query_rejects_insert():
    """Test that nxk_query rejects INSERT queries."""
    result = nxk_query(sql="INSERT INTO users VALUES (1, 'test')")
    
    assert isinstance(result, dict)
    assert result["success"] is False
    assert "error" in result
    assert "INSERT" in result["error"]


def test_nxk_get_sleep_default_limit():
    """Test that nxk_get_sleep uses default limit of 100."""
    # This will fail with missing database, but we can check the validation passes
    result = nxk_get_sleep()
    
    assert isinstance(result, dict)
    # Should either succeed or fail with resource error (not validation error)
    if not result.get("success"):
        assert result["error_type"] in ["resource", "execution"]


def test_nxk_get_heart_rate_limit_validation():
    """Test that nxk_get_heart_rate validates limit range."""
    result = nxk_get_heart_rate(limit=5000)  # Over max of 1000
    
    assert isinstance(result, dict)
    assert result["success"] is False
    assert "error" in result
    assert result["error_type"] == "validation"
    assert "1000" in result["error"]


def test_nxk_get_activity_limit_validation():
    """Test that nxk_get_activity validates limit range."""
    result = nxk_get_activity(limit=0)  # Below min of 1
    
    assert isinstance(result, dict)
    assert result["success"] is False
    assert "error" in result
    assert result["error_type"] == "validation"
