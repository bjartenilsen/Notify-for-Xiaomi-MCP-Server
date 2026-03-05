"""
Unit tests for utility functions.

Tests the TimestampConverter class for various timestamp formats and edge cases.
"""

import pytest
from datetime import datetime
from src.utils import TimestampConverter


class TestTimestampConverter:
    """Test suite for TimestampConverter class."""
    
    def test_convert_seconds_timestamp(self):
        """Test conversion of Unix timestamp in seconds."""
        # 2021-01-01 00:00:00 UTC (adjust for local timezone)
        timestamp = 1609459200
        result = TimestampConverter.convert(timestamp)
        # Result should be in YYYY-MM-DD HH:MM format
        assert len(result) == 16  # "YYYY-MM-DD HH:MM"
        assert result[4] == '-'
        assert result[7] == '-'
        assert result[10] == ' '
        assert result[13] == ':'
    
    def test_convert_milliseconds_timestamp(self):
        """Test conversion of Unix timestamp in milliseconds."""
        # 2021-01-01 00:00:00 UTC in milliseconds
        timestamp = 1609459200000
        result = TimestampConverter.convert(timestamp)
        # Result should be in YYYY-MM-DD HH:MM format
        assert len(result) == 16
        assert result[4] == '-'
        assert result[7] == '-'
        assert result[10] == ' '
        assert result[13] == ':'
    
    def test_milliseconds_detection_threshold(self):
        """Test that timestamps > 10 billion are treated as milliseconds."""
        # Just above threshold (10 billion + 1)
        timestamp_ms = 10_000_000_001
        result = TimestampConverter.convert(timestamp_ms)
        # Should be treated as milliseconds and divided by 1000
        # 10_000_000_001 / 1000 = 10_000_000.001 seconds
        # This is around 1970-04-26
        assert result.startswith('1970-')
    
    def test_seconds_detection_threshold(self):
        """Test that timestamps <= 10 billion are treated as seconds."""
        # Just below threshold
        timestamp_s = 9_999_999_999
        result = TimestampConverter.convert(timestamp_s)
        # Should be treated as seconds
        # This is around 2286-11-20
        assert result.startswith('2286-')
    
    def test_convert_string_timestamp_seconds(self):
        """Test conversion of string timestamp in seconds."""
        timestamp = "1609459200"
        result = TimestampConverter.convert(timestamp)
        assert len(result) == 16
        assert result[4] == '-'
    
    def test_convert_string_timestamp_milliseconds(self):
        """Test conversion of string timestamp in milliseconds."""
        timestamp = "1609459200000"
        result = TimestampConverter.convert(timestamp)
        assert len(result) == 16
        assert result[4] == '-'
    
    def test_convert_float_timestamp(self):
        """Test conversion of float timestamp."""
        timestamp = 1609459200.5
        result = TimestampConverter.convert(timestamp)
        assert len(result) == 16
        assert result[4] == '-'
    
    def test_convert_invalid_string_returns_original(self):
        """Test that invalid string returns original value."""
        timestamp = "not_a_number"
        result = TimestampConverter.convert(timestamp)
        assert result == "not_a_number"
    
    def test_convert_invalid_type_returns_string(self):
        """Test that invalid types return string representation."""
        timestamp = None
        result = TimestampConverter.convert(timestamp)
        assert result == "None"
    
    def test_convert_negative_timestamp_returns_original(self):
        """Test that negative timestamps that fail conversion return original."""
        # Very negative timestamp that might cause OSError
        timestamp = -999999999999999
        result = TimestampConverter.convert(timestamp)
        # Should return string representation
        assert isinstance(result, str)
    
    def test_convert_overflow_timestamp_returns_original(self):
        """Test that overflow timestamps return original value."""
        # Extremely large timestamp that causes overflow
        timestamp = 99999999999999999999
        result = TimestampConverter.convert(timestamp)
        # Should return string representation
        assert isinstance(result, str)
    
    def test_format_matches_specification(self):
        """Test that format exactly matches YYYY-MM-DD HH:MM."""
        timestamp = 1609459200  # 2021-01-01 00:00:00 UTC
        result = TimestampConverter.convert(timestamp)
        
        # Verify format with regex
        import re
        pattern = r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}$'
        assert re.match(pattern, result), f"Format doesn't match: {result}"
    
    def test_local_timezone_conversion(self):
        """Test that conversion uses local timezone."""
        timestamp = 1609459200  # 2021-01-01 00:00:00 UTC
        result = TimestampConverter.convert(timestamp)
        
        # Verify it's a valid datetime string
        dt = datetime.strptime(result, '%Y-%m-%d %H:%M')
        assert dt.year == 2021 or dt.year == 2020  # Might be 2020 in some timezones
    
    def test_recent_timestamp(self):
        """Test conversion of a recent timestamp."""
        # 2024-01-15 12:00:00 UTC
        timestamp = 1705320000
        result = TimestampConverter.convert(timestamp)
        assert '2024-01-' in result
    
    def test_zero_timestamp(self):
        """Test conversion of zero timestamp (Unix epoch)."""
        timestamp = 0
        result = TimestampConverter.convert(timestamp)
        # Should be 1970-01-01 in local timezone
        assert '1970-01-01' in result



class TestQueryValidator:
    """Test suite for QueryValidator class."""
    
    def test_valid_select_query(self):
        """Test that valid SELECT query is accepted."""
        from src.utils import QueryValidator
        
        sql = "SELECT * FROM users"
        is_valid, error = QueryValidator.is_select_only(sql)
        assert is_valid is True
        assert error == ""
    
    def test_select_with_where_clause(self):
        """Test SELECT with WHERE clause is accepted."""
        from src.utils import QueryValidator
        
        sql = "SELECT id, name FROM users WHERE age > 18"
        is_valid, error = QueryValidator.is_select_only(sql)
        assert is_valid is True
        assert error == ""
    
    def test_select_with_join(self):
        """Test SELECT with JOIN is accepted."""
        from src.utils import QueryValidator
        
        sql = "SELECT u.name, o.total FROM users u JOIN orders o ON u.id = o.user_id"
        is_valid, error = QueryValidator.is_select_only(sql)
        assert is_valid is True
        assert error == ""
    
    def test_reject_insert_query(self):
        """Test that INSERT query is rejected."""
        from src.utils import QueryValidator
        
        sql = "INSERT INTO users (name) VALUES ('John')"
        is_valid, error = QueryValidator.is_select_only(sql)
        assert is_valid is False
        assert "INSERT" in error
        assert "Kun SELECT-spørringer er tillatt" in error
    
    def test_reject_update_query(self):
        """Test that UPDATE query is rejected."""
        from src.utils import QueryValidator
        
        sql = "UPDATE users SET name = 'Jane' WHERE id = 1"
        is_valid, error = QueryValidator.is_select_only(sql)
        assert is_valid is False
        assert "UPDATE" in error
    
    def test_reject_delete_query(self):
        """Test that DELETE query is rejected."""
        from src.utils import QueryValidator
        
        sql = "DELETE FROM users WHERE id = 1"
        is_valid, error = QueryValidator.is_select_only(sql)
        assert is_valid is False
        assert "DELETE" in error
    
    def test_reject_drop_query(self):
        """Test that DROP query is rejected."""
        from src.utils import QueryValidator
        
        sql = "DROP TABLE users"
        is_valid, error = QueryValidator.is_select_only(sql)
        assert is_valid is False
        assert "DROP" in error
    
    def test_reject_alter_query(self):
        """Test that ALTER query is rejected."""
        from src.utils import QueryValidator
        
        sql = "ALTER TABLE users ADD COLUMN email VARCHAR(255)"
        is_valid, error = QueryValidator.is_select_only(sql)
        assert is_valid is False
        assert "ALTER" in error
    
    def test_reject_create_query(self):
        """Test that CREATE query is rejected."""
        from src.utils import QueryValidator
        
        sql = "CREATE TABLE users (id INTEGER PRIMARY KEY)"
        is_valid, error = QueryValidator.is_select_only(sql)
        assert is_valid is False
        assert "CREATE" in error
    
    def test_reject_truncate_query(self):
        """Test that TRUNCATE query is rejected."""
        from src.utils import QueryValidator
        
        sql = "TRUNCATE TABLE users"
        is_valid, error = QueryValidator.is_select_only(sql)
        assert is_valid is False
        assert "TRUNCATE" in error
    
    def test_reject_replace_query(self):
        """Test that REPLACE query is rejected."""
        from src.utils import QueryValidator
        
        sql = "REPLACE INTO users (id, name) VALUES (1, 'John')"
        is_valid, error = QueryValidator.is_select_only(sql)
        assert is_valid is False
        assert "REPLACE" in error
    
    def test_reject_pragma_query(self):
        """Test that PRAGMA query is rejected."""
        from src.utils import QueryValidator
        
        sql = "PRAGMA table_info(users)"
        is_valid, error = QueryValidator.is_select_only(sql)
        assert is_valid is False
        assert "PRAGMA" in error
    
    def test_remove_single_line_comments(self):
        """Test that single-line comments are removed before validation."""
        from src.utils import QueryValidator
        
        sql = "SELECT * FROM users -- this is a comment"
        is_valid, error = QueryValidator.is_select_only(sql)
        assert is_valid is True
        assert error == ""
    
    def test_remove_multi_line_comments(self):
        """Test that multi-line comments are removed before validation."""
        from src.utils import QueryValidator
        
        sql = "SELECT * FROM users /* this is a\nmulti-line comment */"
        is_valid, error = QueryValidator.is_select_only(sql)
        assert is_valid is True
        assert error == ""
    
    def test_normalize_whitespace(self):
        """Test that whitespace is normalized."""
        from src.utils import QueryValidator
        
        sql = "  SELECT   *   FROM   users  "
        is_valid, error = QueryValidator.is_select_only(sql)
        assert is_valid is True
        assert error == ""
    
    def test_case_insensitive_select(self):
        """Test that SELECT is case-insensitive."""
        from src.utils import QueryValidator
        
        sql = "select * from users"
        is_valid, error = QueryValidator.is_select_only(sql)
        assert is_valid is True
        assert error == ""
    
    def test_case_insensitive_forbidden_keywords(self):
        """Test that forbidden keywords are case-insensitive."""
        from src.utils import QueryValidator
        
        sql = "insert into users (name) values ('John')"
        is_valid, error = QueryValidator.is_select_only(sql)
        assert is_valid is False
        assert "INSERT" in error
    
    def test_reject_non_select_starting_query(self):
        """Test that query not starting with SELECT is rejected."""
        from src.utils import QueryValidator
        
        sql = "WITH cte AS (SELECT * FROM users) SELECT * FROM cte"
        is_valid, error = QueryValidator.is_select_only(sql)
        assert is_valid is False
        assert "må starte med SELECT" in error
    
    def test_word_boundary_matching(self):
        """Test that keywords are matched with word boundaries."""
        from src.utils import QueryValidator
        
        # "inserted" contains "insert" but should not be rejected
        sql = "SELECT inserted FROM logs"
        is_valid, error = QueryValidator.is_select_only(sql)
        assert is_valid is True
        assert error == ""
    
    def test_forbidden_keyword_in_comment_ignored(self):
        """Test that forbidden keywords in comments are ignored."""
        from src.utils import QueryValidator
        
        sql = "SELECT * FROM users -- DELETE this comment"
        is_valid, error = QueryValidator.is_select_only(sql)
        assert is_valid is True
        assert error == ""
    
    def test_complex_select_query(self):
        """Test complex SELECT query with subqueries."""
        from src.utils import QueryValidator
        
        sql = """
        SELECT u.name, COUNT(o.id) as order_count
        FROM users u
        LEFT JOIN orders o ON u.id = o.user_id
        WHERE u.created_at > '2024-01-01'
        GROUP BY u.name
        HAVING COUNT(o.id) > 5
        ORDER BY order_count DESC
        LIMIT 10
        """
        is_valid, error = QueryValidator.is_select_only(sql)
        assert is_valid is True
        assert error == ""
    
    def test_norwegian_error_message_format(self):
        """Test that error messages are in Norwegian."""
        from src.utils import QueryValidator
        
        sql = "DELETE FROM users"
        is_valid, error = QueryValidator.is_select_only(sql)
        assert is_valid is False
        # Check for Norwegian words
        assert "Kun" in error or "tillatt" in error or "forbudt" in error
    
    def test_empty_query(self):
        """Test that empty query is rejected."""
        from src.utils import QueryValidator
        
        sql = ""
        is_valid, error = QueryValidator.is_select_only(sql)
        assert is_valid is False
        assert "må starte med SELECT" in error
    
    def test_whitespace_only_query(self):
        """Test that whitespace-only query is rejected."""
        from src.utils import QueryValidator
        
        sql = "   \n\t  "
        is_valid, error = QueryValidator.is_select_only(sql)
        assert is_valid is False
        assert "må starte med SELECT" in error
