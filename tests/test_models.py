"""
Unit tests for Pydantic models.

Tests the DateRangeParams base model and its validators.
"""

import pytest
from pydantic import ValidationError

from src.models import DateRangeParams


class TestDateRangeParams:
    """Test suite for DateRangeParams model."""
    
    def test_default_values(self):
        """Test that default values are set correctly."""
        params = DateRangeParams()
        assert params.start_date is None
        assert params.end_date is None
        assert params.limit == 100
    
    def test_valid_date_format(self):
        """Test that valid YYYY-MM-DD dates are accepted."""
        params = DateRangeParams(
            start_date="2024-01-01",
            end_date="2024-12-31"
        )
        assert params.start_date == "2024-01-01"
        assert params.end_date == "2024-12-31"
    
    def test_invalid_date_format_raises_error(self):
        """Test that invalid date formats raise ValidationError with Norwegian message."""
        with pytest.raises(ValidationError) as exc_info:
            DateRangeParams(start_date="01-01-2024")
        
        error = exc_info.value.errors()[0]
        assert "Dato må være i formatet YYYY-MM-DD" in str(error['msg'])
    
    def test_invalid_date_format_end_date(self):
        """Test that invalid end_date format raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            DateRangeParams(end_date="2024/01/01")
        
        error = exc_info.value.errors()[0]
        assert "Dato må være i formatet YYYY-MM-DD" in str(error['msg'])
    
    def test_valid_limit_values(self):
        """Test that valid limit values are accepted."""
        # Minimum limit
        params1 = DateRangeParams(limit=1)
        assert params1.limit == 1
        
        # Maximum limit
        params2 = DateRangeParams(limit=1000)
        assert params2.limit == 1000
        
        # Mid-range limit
        params3 = DateRangeParams(limit=500)
        assert params3.limit == 500
    
    def test_limit_below_minimum_raises_error(self):
        """Test that limit < 1 raises ValidationError with Norwegian message."""
        with pytest.raises(ValidationError) as exc_info:
            DateRangeParams(limit=0)
        
        errors = exc_info.value.errors()
        # Check if error is from ge constraint or custom validator
        assert any("greater than or equal to 1" in str(e['msg']) or 
                   "Grenseverdien må være mellom 1 og 1000" in str(e['msg']) 
                   for e in errors)
    
    def test_limit_above_maximum_raises_error(self):
        """Test that limit > 1000 raises ValidationError with Norwegian message."""
        with pytest.raises(ValidationError) as exc_info:
            DateRangeParams(limit=1001)
        
        errors = exc_info.value.errors()
        # Check if error is from le constraint or custom validator
        assert any("less than or equal to 1000" in str(e['msg']) or 
                   "Grenseverdien må være mellom 1 og 1000" in str(e['msg']) 
                   for e in errors)
    
    def test_none_dates_are_valid(self):
        """Test that None values for dates are accepted."""
        params = DateRangeParams(start_date=None, end_date=None)
        assert params.start_date is None
        assert params.end_date is None
    
    def test_combined_valid_parameters(self):
        """Test that all valid parameters work together."""
        params = DateRangeParams(
            start_date="2024-01-01",
            end_date="2024-12-31",
            limit=50
        )
        assert params.start_date == "2024-01-01"
        assert params.end_date == "2024-12-31"
        assert params.limit == 50
    
    def test_invalid_date_string_formats(self):
        """Test various invalid date string formats."""
        invalid_dates = [
            "24-01-01",      # Two-digit year
            "not-a-date",    # Completely invalid
            "2024/01/01",    # Wrong separator
            "01/01/2024",    # US format
            "2024-01",       # Missing day
            "2024",          # Only year
        ]
        
        for invalid_date in invalid_dates:
            with pytest.raises(ValidationError):
                DateRangeParams(start_date=invalid_date)



class TestSleepParams:
    """Test suite for SleepParams model."""
    
    def test_inherits_from_date_range_params(self):
        """Test that SleepParams inherits all functionality from DateRangeParams."""
        from src.models import SleepParams
        
        params = SleepParams(
            start_date="2024-01-01",
            end_date="2024-12-31",
            limit=50
        )
        assert params.start_date == "2024-01-01"
        assert params.end_date == "2024-12-31"
        assert params.limit == 50
    
    def test_validates_dates(self):
        """Test that SleepParams validates date formats."""
        from src.models import SleepParams
        
        with pytest.raises(ValidationError):
            SleepParams(start_date="invalid-date")
    
    def test_validates_limit(self):
        """Test that SleepParams validates limit range."""
        from src.models import SleepParams
        
        with pytest.raises(ValidationError):
            SleepParams(limit=2000)


class TestHeartRateParams:
    """Test suite for HeartRateParams model."""
    
    def test_inherits_from_date_range_params(self):
        """Test that HeartRateParams inherits all functionality from DateRangeParams."""
        from src.models import HeartRateParams
        
        params = HeartRateParams(
            start_date="2024-01-01",
            end_date="2024-12-31",
            limit=100
        )
        assert params.start_date == "2024-01-01"
        assert params.end_date == "2024-12-31"
        assert params.limit == 100
    
    def test_validates_dates(self):
        """Test that HeartRateParams validates date formats."""
        from src.models import HeartRateParams
        
        with pytest.raises(ValidationError):
            HeartRateParams(end_date="2024/01/01")
    
    def test_validates_limit(self):
        """Test that HeartRateParams validates limit range."""
        from src.models import HeartRateParams
        
        with pytest.raises(ValidationError):
            HeartRateParams(limit=0)


class TestActivityParams:
    """Test suite for ActivityParams model."""
    
    def test_inherits_from_date_range_params(self):
        """Test that ActivityParams inherits all functionality from DateRangeParams."""
        from src.models import ActivityParams
        
        params = ActivityParams(
            start_date="2024-06-01",
            end_date="2024-06-30",
            limit=200
        )
        assert params.start_date == "2024-06-01"
        assert params.end_date == "2024-06-30"
        assert params.limit == 200
    
    def test_validates_dates(self):
        """Test that ActivityParams validates date formats."""
        from src.models import ActivityParams
        
        with pytest.raises(ValidationError):
            ActivityParams(start_date="01-01-2024")
    
    def test_validates_limit(self):
        """Test that ActivityParams validates limit range."""
        from src.models import ActivityParams
        
        with pytest.raises(ValidationError):
            ActivityParams(limit=1001)
    
    def test_default_limit(self):
        """Test that ActivityParams uses default limit of 100."""
        from src.models import ActivityParams
        
        params = ActivityParams()
        assert params.limit == 100



class TestQueryParams:
    """Test suite for QueryParams model."""
    
    def test_valid_select_query(self):
        """Test that valid SELECT queries are accepted."""
        from src.models import QueryParams
        
        params = QueryParams(sql="SELECT * FROM users")
        assert params.sql == "SELECT * FROM users"
    
    def test_valid_select_with_where_clause(self):
        """Test that SELECT queries with WHERE clauses are accepted."""
        from src.models import QueryParams
        
        params = QueryParams(sql="SELECT id, name FROM users WHERE age > 18")
        assert params.sql == "SELECT id, name FROM users WHERE age > 18"
    
    def test_valid_select_with_joins(self):
        """Test that SELECT queries with JOINs are accepted."""
        from src.models import QueryParams
        
        params = QueryParams(sql="SELECT u.name, o.total FROM users u JOIN orders o ON u.id = o.user_id")
        assert params.sql == "SELECT u.name, o.total FROM users u JOIN orders o ON u.id = o.user_id"
    
    def test_insert_query_raises_error(self):
        """Test that INSERT queries are rejected with Norwegian error message."""
        from src.models import QueryParams
        
        with pytest.raises(ValidationError) as exc_info:
            QueryParams(sql="INSERT INTO users (name) VALUES ('test')")
        
        error = exc_info.value.errors()[0]
        assert "Kun SELECT-spørringer er tillatt" in str(error['msg'])
        assert "INSERT" in str(error['msg'])
    
    def test_update_query_raises_error(self):
        """Test that UPDATE queries are rejected with Norwegian error message."""
        from src.models import QueryParams
        
        with pytest.raises(ValidationError) as exc_info:
            QueryParams(sql="UPDATE users SET name = 'test' WHERE id = 1")
        
        error = exc_info.value.errors()[0]
        assert "Kun SELECT-spørringer er tillatt" in str(error['msg'])
        assert "UPDATE" in str(error['msg'])
    
    def test_delete_query_raises_error(self):
        """Test that DELETE queries are rejected with Norwegian error message."""
        from src.models import QueryParams
        
        with pytest.raises(ValidationError) as exc_info:
            QueryParams(sql="DELETE FROM users WHERE id = 1")
        
        error = exc_info.value.errors()[0]
        assert "Kun SELECT-spørringer er tillatt" in str(error['msg'])
        assert "DELETE" in str(error['msg'])
    
    def test_drop_query_raises_error(self):
        """Test that DROP queries are rejected with Norwegian error message."""
        from src.models import QueryParams
        
        with pytest.raises(ValidationError) as exc_info:
            QueryParams(sql="DROP TABLE users")
        
        error = exc_info.value.errors()[0]
        assert "Kun SELECT-spørringer er tillatt" in str(error['msg'])
        assert "DROP" in str(error['msg'])
    
    def test_alter_query_raises_error(self):
        """Test that ALTER queries are rejected with Norwegian error message."""
        from src.models import QueryParams
        
        with pytest.raises(ValidationError) as exc_info:
            QueryParams(sql="ALTER TABLE users ADD COLUMN email VARCHAR(255)")
        
        error = exc_info.value.errors()[0]
        assert "Kun SELECT-spørringer er tillatt" in str(error['msg'])
        assert "ALTER" in str(error['msg'])
    
    def test_create_query_raises_error(self):
        """Test that CREATE queries are rejected with Norwegian error message."""
        from src.models import QueryParams
        
        with pytest.raises(ValidationError) as exc_info:
            QueryParams(sql="CREATE TABLE users (id INT, name VARCHAR(255))")
        
        error = exc_info.value.errors()[0]
        assert "Kun SELECT-spørringer er tillatt" in str(error['msg'])
        assert "CREATE" in str(error['msg'])
    
    def test_empty_sql_raises_error(self):
        """Test that empty SQL string raises ValidationError."""
        from src.models import QueryParams
        
        with pytest.raises(ValidationError) as exc_info:
            QueryParams(sql="")
        
        # Should fail min_length validation
        error = exc_info.value.errors()[0]
        assert "at least 1 character" in str(error['msg']) or "min_length" in str(error['type'])
    
    def test_non_select_query_raises_error(self):
        """Test that queries not starting with SELECT are rejected."""
        from src.models import QueryParams
        
        with pytest.raises(ValidationError) as exc_info:
            QueryParams(sql="SHOW TABLES")
        
        error = exc_info.value.errors()[0]
        assert "Spørringen må starte med SELECT" in str(error['msg'])
    
    def test_select_with_comments_is_valid(self):
        """Test that SELECT queries with comments are accepted."""
        from src.models import QueryParams
        
        params = QueryParams(sql="-- This is a comment\nSELECT * FROM users")
        assert "SELECT * FROM users" in params.sql
    
    def test_lowercase_select_is_valid(self):
        """Test that lowercase SELECT queries are accepted."""
        from src.models import QueryParams
        
        params = QueryParams(sql="select * from users")
        assert params.sql == "select * from users"
    
    def test_mixed_case_select_is_valid(self):
        """Test that mixed case SELECT queries are accepted."""
        from src.models import QueryParams
        
        params = QueryParams(sql="SeLeCt * FrOm users")
        assert params.sql == "SeLeCt * FrOm users"
