"""
Error handling and Norwegian message catalog for Notify Xiaomi MCP Server.

This module provides centralized error message management with all messages
in Norwegian, along with helper functions for creating consistent error responses.

Requirements: 1.5, 2.4, 7.5, 9.4, 11.3, 12.1, 12.2, 12.3, 12.4, 12.5
"""

from typing import Optional


# Norwegian error message catalog
ERROR_MESSAGES = {
    # Authentication errors (Requirements: 1.5, 12.4)
    "auth_no_credentials": (
        "Fant ikke credentials.json på {path}. "
        "Last ned OAuth2-legitimasjon fra Google Cloud Console og "
        "plasser den i ~/.notify-xiaomi-mcp/"
    ),
    "auth_failed": (
        "Google Drive-autentisering feilet: {error}. "
        "Sjekk at credentials.json er riktig konfigurert."
    ),
    "auth_token_load_failed": (
        "Kunne ikke laste token.pickle: {error}. "
        "Prøv å slette filen og autentiser på nytt."
    ),
    "auth_token_refresh_failed": (
        "Kunne ikke fornye tilgangstokenet: {error}. "
        "Prøv å slette token.pickle og autentiser på nytt."
    ),
    "auth_token_save_failed": (
        "Kunne ikke lagre token.pickle: {error}. "
        "Sjekk at katalogen ~/.notify-xiaomi-mcp/ er skrivbar."
    ),
    "auth_service_creation_failed": (
        "Kunne ikke opprette Google Drive-tjeneste: {error}"
    ),
    "auth_service_not_initialized": (
        "Google Drive-tjenesten er ikke initialisert. "
        "Kjør authenticate() først."
    ),
    
    # Resource errors (Requirements: 2.4, 3.5, 12.3)
    "db_not_found": (
        "Databasen ble ikke funnet. "
        "Kjør nxk_sync_database først for å laste ned databasen."
    ),
    "folder_not_found": (
        "Fant ikke mappen '{folder_name}' i Google Drive."
    ),
    "file_not_found": (
        "Fant ikke filen '{filename}' i mappen."
    ),
    "file_write_failed": (
        "Kunne ikke skrive til {path}: {error}. "
        "Sjekk at katalogen eksisterer og er skrivbar."
    ),
    
    # Google Drive errors (Requirements: 2.4)
    "drive_search_failed": (
        "Feil ved søk i Google Drive: {error}. "
        "Sjekk at du har tilgang til Google Drive."
    ),
    "drive_search_unexpected": (
        "Uventet feil ved søk etter mappe: {error}"
    ),
    "drive_download_failed": (
        "Feil ved nedlasting fra Google Drive: {error}. "
        "Sjekk at du har tilgang til filen."
    ),
    "drive_download_unexpected": (
        "Uventet feil ved nedlasting av fil: {error}"
    ),
    
    # Validation errors (Requirements: 11.3)
    "invalid_date_format": (
        "Dato må være i formatet YYYY-MM-DD"
    ),
    "invalid_limit": (
        "Grenseverdien må være mellom 1 og 1000"
    ),
    "missing_required_param": (
        "Mangler påkrevd parameter: {param}"
    ),
    "query_not_select": (
        "Kun SELECT-spørringer er tillatt. Fant forbudt nøkkelord: {keyword}"
    ),
    "query_must_start_with_select": (
        "Spørringen må starte med SELECT"
    ),
    
    # Execution errors (Requirements: 7.5, 9.4, 12.5)
    "db_read_error": (
        "Kunne ikke lese fra databasen: {error}"
    ),
    "query_execution_failed": (
        "SQL-spørring feilet: {error}"
    ),
    "sleep_data_fetch_failed": (
        "Kunne ikke hente søvndata: {error}"
    ),
    "heart_rate_fetch_failed": (
        "Kunne ikke hente pulsdata: {error}"
    ),
    "activity_data_fetch_failed": (
        "Kunne ikke hente aktivitetsdata: {error}"
    ),
    "sync_unexpected_error": (
        "Uventet feil ved synkronisering: {error}"
    ),
    "unexpected_error": (
        "Uventet feil: {error}"
    ),
}


def get_error_message(key: str, **kwargs) -> str:
    """
    Get Norwegian error message with optional formatting.
    
    This function retrieves an error message from the ERROR_MESSAGES catalog
    and formats it with the provided keyword arguments.
    
    Args:
        key: Error message key from ERROR_MESSAGES dictionary
        **kwargs: Optional formatting parameters for the error message
    
    Returns:
        Formatted Norwegian error message
    
    Raises:
        KeyError: If the error message key doesn't exist
    
    Examples:
        >>> get_error_message("folder_not_found", folder_name="My Folder")
        "Fant ikke mappen 'My Folder' i Google Drive."
        
        >>> get_error_message("db_not_found")
        "Databasen ble ikke funnet. Kjør nxk_sync_database først..."
    
    Requirements: 12.1, 12.2
    """
    message_template = ERROR_MESSAGES[key]
    return message_template.format(**kwargs)


def create_error_response(
    error_type: str,
    message: str,
    details: Optional[str] = None
) -> dict:
    """
    Create a standardized error response dictionary.
    
    All error responses follow a consistent structure with:
    - success: Always False for errors
    - error: Norwegian error message
    - error_type: Category of error (auth, resource, validation, execution)
    - details: Optional technical details for debugging
    
    Args:
        error_type: Error category - one of: "auth", "resource", "validation", "execution"
        message: Norwegian error message describing what went wrong
        details: Optional technical details (e.g., exception message)
    
    Returns:
        Dictionary with standardized error response structure
    
    Examples:
        >>> create_error_response("auth", "Autentisering feilet")
        {'success': False, 'error': 'Autentisering feilet', 'error_type': 'auth'}
        
        >>> create_error_response("validation", "Ugyldig dato", details="ValueError: ...")
        {'success': False, 'error': 'Ugyldig dato', 'error_type': 'validation', 'details': 'ValueError: ...'}
    
    Requirements: 12.1, 12.2
    """
    response = {
        "success": False,
        "error": message,
        "error_type": error_type
    }
    
    if details is not None:
        response["details"] = details
    
    return response


def create_success_response(data: dict) -> dict:
    """
    Create a standardized success response dictionary.
    
    All success responses include success=True and merge in the provided data.
    
    Args:
        data: Dictionary containing response data
    
    Returns:
        Dictionary with success=True and merged data
    
    Examples:
        >>> create_success_response({"count": 5, "records": []})
        {'success': True, 'count': 5, 'records': []}
    
    Requirements: 12.1
    """
    return {"success": True, **data}
