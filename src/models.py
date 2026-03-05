"""
Pydantic models for input validation in Notify Xiaomi MCP Server.

This module defines data models for validating tool inputs using Pydantic v2.
All validation error messages are in Norwegian as per requirements.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class DateRangeParams(BaseModel):
    """
    Base model for date range queries.
    
    This model provides common parameters for querying health data (sleep, 
    heart rate, activity) with date range filtering and result limiting.
    
    Attributes:
        start_date: Optional start date in YYYY-MM-DD format
        end_date: Optional end date in YYYY-MM-DD format
        limit: Maximum number of records to return (1-1000, default 100)
    """
    
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
        description="Maximum number of records (1-1000)"
    )
    
    @field_validator('start_date', 'end_date')
    @classmethod
    def validate_date_format(cls, v: Optional[str]) -> Optional[str]:
        """
        Validate that date string matches YYYY-MM-DD format.
        
        Args:
            v: Date string to validate
        
        Returns:
            The validated date string
        
        Raises:
            ValueError: If date format is invalid (Norwegian error message)
        """
        if v is None:
            return v
        
        try:
            datetime.strptime(v, '%Y-%m-%d')
            return v
        except ValueError:
            raise ValueError('Dato må være i formatet YYYY-MM-DD')
    
    @field_validator('limit')
    @classmethod
    def validate_limit(cls, v: Optional[int]) -> Optional[int]:
        """
        Validate that limit is within acceptable range (1-1000).
        
        Args:
            v: Limit value to validate
        
        Returns:
            The validated limit value
        
        Raises:
            ValueError: If limit is outside valid range (Norwegian error message)
        """
        if v is None:
            return 100  # Default value
        
        if v < 1 or v > 1000:
            raise ValueError('Grenseverdien må være mellom 1 og 1000')
        
        return v


class SleepParams(DateRangeParams):
    """
    Parameters for sleep data queries.
    
    Inherits all validation from DateRangeParams:
    - start_date: Optional start date filter (YYYY-MM-DD)
    - end_date: Optional end date filter (YYYY-MM-DD)
    - limit: Maximum records to return (1-1000, default 100)
    """
    pass


class HeartRateParams(DateRangeParams):
    """
    Parameters for heart rate data queries.
    
    Inherits all validation from DateRangeParams:
    - start_date: Optional start date filter (YYYY-MM-DD)
    - end_date: Optional end date filter (YYYY-MM-DD)
    - limit: Maximum records to return (1-1000, default 100)
    """
    pass


class ActivityParams(DateRangeParams):
    """
    Parameters for activity data queries.
    
    Inherits all validation from DateRangeParams:
    - start_date: Optional start date filter (YYYY-MM-DD)
    - end_date: Optional end date filter (YYYY-MM-DD)
    - limit: Maximum records to return (1-1000, default 100)
    """
    pass



class QueryParams(BaseModel):
    """
    Parameters for custom SQL queries.
    
    This model validates SQL queries to ensure only SELECT statements are
    executed against the database, protecting it from write operations.
    
    Attributes:
        sql: SQL SELECT statement (minimum 1 character)
    """
    
    sql: str = Field(
        ..., 
        min_length=1, 
        description="SQL SELECT statement"
    )
    
    @field_validator('sql')
    @classmethod
    def validate_select_only(cls, v: str) -> str:
        """
        Validate that SQL query contains only SELECT statement.
        
        Uses QueryValidator.is_select_only() to check for forbidden keywords
        (INSERT, UPDATE, DELETE, DROP, ALTER, CREATE, TRUNCATE, REPLACE, PRAGMA)
        and ensure the query starts with SELECT.
        
        Args:
            v: SQL query string to validate
        
        Returns:
            The validated SQL query string
        
        Raises:
            ValueError: If query contains forbidden keywords or doesn't start 
                       with SELECT (Norwegian error message)
        """
        from .utils import QueryValidator
        
        is_valid, error_message = QueryValidator.is_select_only(v)
        
        if not is_valid:
            raise ValueError(error_message)
        
        return v
