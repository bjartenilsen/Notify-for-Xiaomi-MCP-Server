"""
Utility functions for Notify Xiaomi MCP Server.

This module provides helper functions for timestamp conversion and other utilities.
"""

from datetime import datetime
from typing import Union


class TimestampConverter:
    """
    Converts Unix timestamps to human-readable format.
    
    Handles both seconds and milliseconds timestamps, automatically detecting
    the format based on the magnitude of the value.
    """
    
    @staticmethod
    def convert(timestamp: Union[int, float, str]) -> str:
        """
        Convert Unix timestamp to YYYY-MM-DD HH:MM format.
        
        Automatically detects whether the timestamp is in seconds or milliseconds
        based on a threshold of 10 billion. Timestamps greater than 10 billion
        are treated as milliseconds and divided by 1000.
        
        Args:
            timestamp: Unix timestamp in seconds or milliseconds, or a string
        
        Returns:
            Formatted timestamp string in YYYY-MM-DD HH:MM format in local timezone.
            If conversion fails, returns the original value as a string.
        
        Examples:
            >>> TimestampConverter.convert(1609459200)
            '2021-01-01 00:00'
            >>> TimestampConverter.convert(1609459200000)
            '2021-01-01 00:00'
            >>> TimestampConverter.convert("invalid")
            'invalid'
        """
        try:
            # Handle string input - try to convert to float
            if isinstance(timestamp, str):
                timestamp = float(timestamp)
            
            # Detect milliseconds vs seconds
            # Threshold: 10 billion (10,000,000,000)
            # Timestamps after year 2000 in seconds are > 946684800
            # If timestamp > 10 billion, it's in milliseconds
            if timestamp > 10_000_000_000:
                timestamp = timestamp / 1000
            
            # Convert to datetime object in local timezone
            dt = datetime.fromtimestamp(timestamp)
            
            # Format as YYYY-MM-DD HH:MM
            return dt.strftime('%Y-%m-%d %H:%M')
        
        except (ValueError, OSError, OverflowError, TypeError):
            # Return original value as string if conversion fails
            return str(timestamp)


class QueryValidator:
    """
    Validates SQL queries to ensure only SELECT statements are executed.
    
    This validator protects the database from write operations by rejecting
    any queries containing INSERT, UPDATE, DELETE, DROP, ALTER, CREATE, 
    TRUNCATE, REPLACE, or PRAGMA keywords.
    """
    
    @staticmethod
    def is_select_only(sql: str) -> tuple[bool, str]:
        """
        Check if SQL query contains only SELECT statement.
        
        This method:
        1. Removes SQL comments (-- and /* */)
        2. Normalizes whitespace and converts to uppercase
        3. Checks for forbidden keywords
        4. Verifies query starts with SELECT
        
        Args:
            sql: SQL query string to validate
        
        Returns:
            Tuple of (is_valid, error_message):
            - is_valid: True if query is SELECT-only, False otherwise
            - error_message: Norwegian error message if invalid, empty string if valid
        
        Examples:
            >>> QueryValidator.is_select_only("SELECT * FROM users")
            (True, '')
            >>> QueryValidator.is_select_only("DELETE FROM users")
            (False, 'Kun SELECT-spørringer er tillatt. Fant forbudt nøkkelord: DELETE')
        """
        import re
        
        # Remove SQL comments
        # Remove single-line comments (-- comment)
        sql_clean = re.sub(r'--.*$', '', sql, flags=re.MULTILINE)
        # Remove multi-line comments (/* comment */)
        sql_clean = re.sub(r'/\*.*?\*/', '', sql_clean, flags=re.DOTALL)
        
        # Normalize whitespace and convert to uppercase
        sql_normalized = ' '.join(sql_clean.strip().split()).upper()
        
        # Check for forbidden keywords
        forbidden_keywords = [
            'INSERT', 'UPDATE', 'DELETE', 'DROP', 'ALTER',
            'CREATE', 'TRUNCATE', 'REPLACE', 'PRAGMA'
        ]
        
        for keyword in forbidden_keywords:
            # Use word boundary to match whole words only
            if re.search(rf'\b{keyword}\b', sql_normalized):
                return False, f"Kun SELECT-spørringer er tillatt. Fant forbudt nøkkelord: {keyword}"
        
        # Verify query starts with SELECT
        if not sql_normalized.startswith('SELECT'):
            return False, "Spørringen må starte med SELECT"
        
        return True, ""
