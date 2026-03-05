"""
Tests for error handling and Norwegian message catalog.

This module tests the centralized error handling functions and message catalog
to ensure consistent Norwegian error messages across the application.

Requirements: 1.5, 2.4, 7.5, 9.4, 11.3, 12.1, 12.2, 12.3, 12.4, 12.5
"""

import pytest

from src.error_handling import (
    ERROR_MESSAGES,
    get_error_message,
    create_error_response,
    create_success_response,
)


class TestErrorMessages:
    """Test the ERROR_MESSAGES catalog."""
    
    def test_error_messages_dict_exists(self):
        """Test that ERROR_MESSAGES dictionary exists and is not empty."""
        assert ERROR_MESSAGES is not None
        assert len(ERROR_MESSAGES) > 0
    
    def test_all_error_messages_are_norwegian(self):
        """Test that all error messages contain Norwegian words."""
        norwegian_indicators = [
            'feilet', 'ikke', 'fant', 'ugyldig', 'må', 'kunne',
            'Fant', 'Kunne', 'Kjør', 'Sjekk', 'Prøv', 'Last',
            'Uventet', 'ved', 'til', 'fra', 'eller', 'og',
            'Mangler', 'påkrevd', 'parameter', 'Kun', 'tillatt'
        ]
        
        for key, message in ERROR_MESSAGES.items():
            # Each message should contain at least one Norwegian indicator
            has_norwegian = any(word in message for word in norwegian_indicators)
            assert has_norwegian, f"Message '{key}' may not be in Norwegian: {message}"
    
    def test_auth_error_messages_exist(self):
        """Test that all authentication error messages exist."""
        auth_keys = [
            "auth_no_credentials",
            "auth_failed",
            "auth_token_load_failed",
            "auth_token_refresh_failed",
            "auth_token_save_failed",
            "auth_service_creation_failed",
            "auth_service_not_initialized",
        ]
        
        for key in auth_keys:
            assert key in ERROR_MESSAGES, f"Missing auth error message: {key}"
    
    def test_resource_error_messages_exist(self):
        """Test that all resource error messages exist."""
        resource_keys = [
            "db_not_found",
            "folder_not_found",
            "file_not_found",
            "file_write_failed",
        ]
        
        for key in resource_keys:
            assert key in ERROR_MESSAGES, f"Missing resource error message: {key}"
    
    def test_validation_error_messages_exist(self):
        """Test that all validation error messages exist."""
        validation_keys = [
            "invalid_date_format",
            "invalid_limit",
            "missing_required_param",
            "query_not_select",
            "query_must_start_with_select",
        ]
        
        for key in validation_keys:
            assert key in ERROR_MESSAGES, f"Missing validation error message: {key}"
    
    def test_execution_error_messages_exist(self):
        """Test that all execution error messages exist."""
        execution_keys = [
            "db_read_error",
            "query_execution_failed",
            "sleep_data_fetch_failed",
            "heart_rate_fetch_failed",
            "activity_data_fetch_failed",
            "sync_unexpected_error",
            "unexpected_error",
        ]
        
        for key in execution_keys:
            assert key in ERROR_MESSAGES, f"Missing execution error message: {key}"
    
    def test_db_not_found_mentions_sync_tool(self):
        """Test that db_not_found error mentions nxk_sync_database (Requirement 12.3)."""
        message = ERROR_MESSAGES["db_not_found"]
        assert "nxk_sync_database" in message


class TestGetErrorMessage:
    """Test the get_error_message() helper function."""
    
    def test_get_error_message_without_formatting(self):
        """Test getting error message without formatting parameters."""
        message = get_error_message("db_not_found")
        assert isinstance(message, str)
        assert len(message) > 0
        assert "nxk_sync_database" in message
    
    def test_get_error_message_with_single_parameter(self):
        """Test getting error message with single formatting parameter."""
        message = get_error_message("folder_not_found", folder_name="Test Folder")
        assert "Test Folder" in message
        assert "Fant ikke mappen" in message
    
    def test_get_error_message_with_multiple_parameters(self):
        """Test getting error message with multiple formatting parameters."""
        message = get_error_message(
            "file_write_failed",
            path="/test/path",
            error="Permission denied"
        )
        assert "/test/path" in message
        assert "Permission denied" in message
    
    def test_get_error_message_invalid_key_raises_error(self):
        """Test that invalid error key raises KeyError."""
        with pytest.raises(KeyError):
            get_error_message("nonexistent_error_key")
    
    def test_get_error_message_auth_no_credentials(self):
        """Test auth_no_credentials message formatting."""
        message = get_error_message("auth_no_credentials", path="/test/credentials.json")
        assert "/test/credentials.json" in message
        assert "credentials.json" in message
        assert "OAuth2" in message
    
    def test_get_error_message_query_not_select(self):
        """Test query_not_select message formatting."""
        message = get_error_message("query_not_select", keyword="DELETE")
        assert "DELETE" in message
        assert "SELECT" in message


class TestCreateErrorResponse:
    """Test the create_error_response() helper function."""
    
    def test_create_error_response_basic(self):
        """Test creating basic error response without details."""
        response = create_error_response("auth", "Autentisering feilet")
        
        assert response["success"] is False
        assert response["error"] == "Autentisering feilet"
        assert response["error_type"] == "auth"
        assert "details" not in response
    
    def test_create_error_response_with_details(self):
        """Test creating error response with technical details."""
        response = create_error_response(
            "execution",
            "Database feil",
            details="SQLite error: table not found"
        )
        
        assert response["success"] is False
        assert response["error"] == "Database feil"
        assert response["error_type"] == "execution"
        assert response["details"] == "SQLite error: table not found"
    
    def test_create_error_response_all_error_types(self):
        """Test creating error responses for all error types."""
        error_types = ["auth", "resource", "validation", "execution"]
        
        for error_type in error_types:
            response = create_error_response(error_type, f"Test {error_type} error")
            assert response["error_type"] == error_type
            assert response["success"] is False
    
    def test_create_error_response_structure(self):
        """Test that error response has correct structure."""
        response = create_error_response("validation", "Ugyldig input")
        
        # Check required fields
        assert "success" in response
        assert "error" in response
        assert "error_type" in response
        
        # Check field types
        assert isinstance(response["success"], bool)
        assert isinstance(response["error"], str)
        assert isinstance(response["error_type"], str)


class TestCreateSuccessResponse:
    """Test the create_success_response() helper function."""
    
    def test_create_success_response_basic(self):
        """Test creating basic success response."""
        response = create_success_response({"count": 5})
        
        assert response["success"] is True
        assert response["count"] == 5
    
    def test_create_success_response_with_multiple_fields(self):
        """Test creating success response with multiple data fields."""
        data = {
            "records": [{"id": 1}, {"id": 2}],
            "count": 2,
            "message": "Success"
        }
        response = create_success_response(data)
        
        assert response["success"] is True
        assert response["records"] == [{"id": 1}, {"id": 2}]
        assert response["count"] == 2
        assert response["message"] == "Success"
    
    def test_create_success_response_empty_data(self):
        """Test creating success response with empty data."""
        response = create_success_response({})
        
        assert response["success"] is True
        assert len(response) == 1  # Only success field
    
    def test_create_success_response_preserves_all_data(self):
        """Test that all data fields are preserved in success response."""
        data = {
            "field1": "value1",
            "field2": 123,
            "field3": [1, 2, 3],
            "field4": {"nested": "data"}
        }
        response = create_success_response(data)
        
        assert response["success"] is True
        for key, value in data.items():
            assert response[key] == value


class TestErrorHandlingIntegration:
    """Integration tests for error handling functions."""
    
    def test_complete_error_flow_auth(self):
        """Test complete error flow for authentication error."""
        # Get error message
        error_msg = get_error_message("auth_failed", error="Invalid credentials")
        
        # Create error response
        response = create_error_response("auth", error_msg)
        
        # Verify response structure
        assert response["success"] is False
        assert "Invalid credentials" in response["error"]
        assert response["error_type"] == "auth"
    
    def test_complete_error_flow_resource(self):
        """Test complete error flow for resource error."""
        # Get error message
        error_msg = get_error_message("db_not_found")
        
        # Create error response
        response = create_error_response("resource", error_msg)
        
        # Verify response structure
        assert response["success"] is False
        assert "nxk_sync_database" in response["error"]
        assert response["error_type"] == "resource"
    
    def test_complete_error_flow_validation(self):
        """Test complete error flow for validation error."""
        # Get error message
        error_msg = get_error_message("invalid_date_format")
        
        # Create error response
        response = create_error_response("validation", error_msg)
        
        # Verify response structure
        assert response["success"] is False
        assert "YYYY-MM-DD" in response["error"]
        assert response["error_type"] == "validation"
    
    def test_complete_success_flow(self):
        """Test complete success flow."""
        # Create success response
        response = create_success_response({
            "records": [{"id": 1}],
            "count": 1
        })
        
        # Verify response structure
        assert response["success"] is True
        assert response["count"] == 1
        assert len(response["records"]) == 1
