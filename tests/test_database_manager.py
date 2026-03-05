"""
Unit tests for DatabaseManager class.

Tests the read-only database connection functionality.
"""

import sqlite3
import tempfile
from pathlib import Path

import pytest

from src.database_manager import DatabaseManager


class TestDatabaseManager:
    """Test suite for DatabaseManager class."""
    
    def test_get_readonly_connection_returns_connection(self):
        """Test that get_readonly_connection returns a valid connection."""
        # Create a temporary database file
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            tmp_path = Path(tmp.name)
        
        try:
            # Create a simple database
            conn = sqlite3.connect(str(tmp_path))
            conn.execute("CREATE TABLE test (id INTEGER PRIMARY KEY, name TEXT)")
            conn.execute("INSERT INTO test (name) VALUES ('test_data')")
            conn.commit()
            conn.close()
            
            # Test DatabaseManager
            db_manager = DatabaseManager(tmp_path)
            conn = db_manager.get_readonly_connection()
            
            # Verify connection is valid
            assert conn is not None
            assert isinstance(conn, sqlite3.Connection)
            
            # Verify we can read data
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM test")
            rows = cursor.fetchall()
            assert len(rows) == 1
            
            conn.close()
        finally:
            # Clean up
            tmp_path.unlink()
    
    def test_get_readonly_connection_sets_row_factory(self):
        """Test that row_factory is set to sqlite3.Row for dict-like access."""
        # Create a temporary database file
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            tmp_path = Path(tmp.name)
        
        try:
            # Create a simple database
            conn = sqlite3.connect(str(tmp_path))
            conn.execute("CREATE TABLE test (id INTEGER PRIMARY KEY, name TEXT)")
            conn.execute("INSERT INTO test (name) VALUES ('test_data')")
            conn.commit()
            conn.close()
            
            # Test DatabaseManager
            db_manager = DatabaseManager(tmp_path)
            conn = db_manager.get_readonly_connection()
            
            # Verify row_factory is set
            assert conn.row_factory == sqlite3.Row
            
            # Verify dict-like access works
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM test")
            row = cursor.fetchone()
            
            # Access by column name (dict-like)
            assert row['name'] == 'test_data'
            assert row['id'] == 1
            
            conn.close()
        finally:
            # Clean up
            tmp_path.unlink()
    
    def test_get_readonly_connection_prevents_writes(self):
        """Test that read-only connection prevents write operations."""
        # Create a temporary database file
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            tmp_path = Path(tmp.name)
        
        try:
            # Create a simple database
            conn = sqlite3.connect(str(tmp_path))
            conn.execute("CREATE TABLE test (id INTEGER PRIMARY KEY, name TEXT)")
            conn.commit()
            conn.close()
            
            # Test DatabaseManager
            db_manager = DatabaseManager(tmp_path)
            conn = db_manager.get_readonly_connection()
            
            # Attempt to write should raise an error
            with pytest.raises(sqlite3.OperationalError) as exc_info:
                conn.execute("INSERT INTO test (name) VALUES ('should_fail')")
            
            # Verify error message indicates read-only mode
            assert "readonly" in str(exc_info.value).lower() or "attempt to write" in str(exc_info.value).lower()
            
            conn.close()
        finally:
            # Clean up
            tmp_path.unlink()
    
    def test_get_readonly_connection_fails_on_missing_database(self):
        """Test that connection fails gracefully when database doesn't exist."""
        # Use a non-existent path
        non_existent_path = Path("/tmp/non_existent_database_12345.db")
        
        db_manager = DatabaseManager(non_existent_path)
        
        # Should raise OperationalError for missing file
        with pytest.raises(sqlite3.OperationalError):
            db_manager.get_readonly_connection()

    def test_exists_returns_true_when_database_exists(self):
        """Test that exists() returns True when database file exists."""
        # Create a temporary database file
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            tmp_path = Path(tmp.name)
        
        try:
            # Create a simple database
            conn = sqlite3.connect(str(tmp_path))
            conn.execute("CREATE TABLE test (id INTEGER PRIMARY KEY)")
            conn.commit()
            conn.close()
            
            # Test DatabaseManager
            db_manager = DatabaseManager(tmp_path)
            assert db_manager.exists() is True
        finally:
            # Clean up
            tmp_path.unlink()
    
    def test_exists_returns_false_when_database_missing(self):
        """Test that exists() returns False when database file doesn't exist."""
        non_existent_path = Path("/tmp/non_existent_database_12345.db")
        db_manager = DatabaseManager(non_existent_path)
        assert db_manager.exists() is False
    
    def test_get_tables_returns_table_information(self):
        """Test that get_tables() returns complete table information."""
        # Create a temporary database file
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            tmp_path = Path(tmp.name)
        
        try:
            # Create a database with multiple tables
            conn = sqlite3.connect(str(tmp_path))
            conn.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT, age INTEGER)")
            conn.execute("CREATE TABLE posts (id INTEGER PRIMARY KEY, title TEXT)")
            conn.execute("INSERT INTO users (name, age) VALUES ('Alice', 30)")
            conn.execute("INSERT INTO users (name, age) VALUES ('Bob', 25)")
            conn.execute("INSERT INTO posts (title) VALUES ('First Post')")
            conn.commit()
            conn.close()
            
            # Test DatabaseManager
            db_manager = DatabaseManager(tmp_path)
            tables = db_manager.get_tables()
            
            # Verify we got both tables
            assert len(tables) == 2
            
            # Find users table
            users_table = next(t for t in tables if t['name'] == 'users')
            assert users_table['row_count'] == 2
            assert len(users_table['columns']) == 3
            
            # Verify column information
            column_names = [col['name'] for col in users_table['columns']]
            assert 'id' in column_names
            assert 'name' in column_names
            assert 'age' in column_names
            
            # Find posts table
            posts_table = next(t for t in tables if t['name'] == 'posts')
            assert posts_table['row_count'] == 1
            assert len(posts_table['columns']) == 2
        finally:
            # Clean up
            tmp_path.unlink()
    
    def test_execute_query_returns_results(self):
        """Test that execute_query() executes SELECT and returns results."""
        # Create a temporary database file
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            tmp_path = Path(tmp.name)
        
        try:
            # Create a database with test data
            conn = sqlite3.connect(str(tmp_path))
            conn.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT, age INTEGER)")
            conn.execute("INSERT INTO users (name, age) VALUES ('Alice', 30)")
            conn.execute("INSERT INTO users (name, age) VALUES ('Bob', 25)")
            conn.commit()
            conn.close()
            
            # Test DatabaseManager
            db_manager = DatabaseManager(tmp_path)
            results = db_manager.execute_query("SELECT * FROM users WHERE age > 26")
            
            # Verify results
            assert len(results) == 1
            assert results[0]['name'] == 'Alice'
            assert results[0]['age'] == 30
        finally:
            # Clean up
            tmp_path.unlink()
    
    def test_execute_query_with_parameters(self):
        """Test that execute_query() works with named parameters."""
        # Create a temporary database file
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            tmp_path = Path(tmp.name)
        
        try:
            # Create a database with test data
            conn = sqlite3.connect(str(tmp_path))
            conn.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT, age INTEGER)")
            conn.execute("INSERT INTO users (name, age) VALUES ('Alice', 30)")
            conn.execute("INSERT INTO users (name, age) VALUES ('Bob', 25)")
            conn.commit()
            conn.close()
            
            # Test DatabaseManager
            db_manager = DatabaseManager(tmp_path)
            results = db_manager.execute_query(
                "SELECT * FROM users WHERE age > :min_age",
                params={'min_age': 26}
            )
            
            # Verify results
            assert len(results) == 1
            assert results[0]['name'] == 'Alice'
        finally:
            # Clean up
            tmp_path.unlink()
    
    def test_get_sleep_data_returns_records(self):
        """Test that get_sleep_data() returns sleep records with converted timestamps."""
        # Create a temporary database file
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            tmp_path = Path(tmp.name)
        
        try:
            # Create a database with sleep data
            conn = sqlite3.connect(str(tmp_path))
            conn.execute("CREATE TABLE SLEEP_DATA (id INTEGER PRIMARY KEY, start INTEGER, stop INTEGER, deep INTEGER, light INTEGER)")
            # Use timestamps: Jan 1, 2024 22:00 to Jan 2, 2024 06:00
            conn.execute("INSERT INTO SLEEP_DATA (start, stop, deep, light) VALUES (1704142800, 1704171600, 180, 300)")
            # Use timestamps: Jan 2, 2024 22:00 to Jan 3, 2024 06:00
            conn.execute("INSERT INTO SLEEP_DATA (start, stop, deep, light) VALUES (1704229200, 1704258000, 200, 280)")
            conn.commit()
            conn.close()
            
            # Test DatabaseManager
            db_manager = DatabaseManager(tmp_path)
            results = db_manager.get_sleep_data()
            
            # Verify results
            assert len(results) == 2
            # Results should be ordered by start DESC
            assert 'start' in results[0]
            assert 'stop' in results[0]
            # Timestamps should be converted to readable format
            assert isinstance(results[0]['start'], str)
            assert '-' in results[0]['start']  # Should contain date separator
        finally:
            # Clean up
            tmp_path.unlink()
    
    def test_get_sleep_data_with_date_filters(self):
        """Test that get_sleep_data() filters by date range."""
        # Create a temporary database file
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            tmp_path = Path(tmp.name)
        
        try:
            # Create a database with sleep data
            conn = sqlite3.connect(str(tmp_path))
            conn.execute("CREATE TABLE SLEEP_DATA (id INTEGER PRIMARY KEY, start INTEGER, stop INTEGER)")
            # Jan 1, 2024
            conn.execute("INSERT INTO SLEEP_DATA (start, stop) VALUES (1704142800, 1704171600)")
            # Jan 5, 2024
            conn.execute("INSERT INTO SLEEP_DATA (start, stop) VALUES (1704488400, 1704517200)")
            # Jan 10, 2024
            conn.execute("INSERT INTO SLEEP_DATA (start, stop) VALUES (1704920400, 1704949200)")
            conn.commit()
            conn.close()
            
            # Test DatabaseManager with date filter
            db_manager = DatabaseManager(tmp_path)
            results = db_manager.get_sleep_data(start_date='2024-01-05', end_date='2024-01-10')
            
            # Should only get records from Jan 5 and Jan 10
            assert len(results) == 2
        finally:
            # Clean up
            tmp_path.unlink()
    
    def test_get_sleep_data_respects_limit(self):
        """Test that get_sleep_data() respects the limit parameter."""
        # Create a temporary database file
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            tmp_path = Path(tmp.name)
        
        try:
            # Create a database with multiple sleep records
            conn = sqlite3.connect(str(tmp_path))
            conn.execute("CREATE TABLE SLEEP_DATA (id INTEGER PRIMARY KEY, start INTEGER, stop INTEGER)")
            for i in range(10):
                timestamp = 1704142800 + (i * 86400)  # One day apart
                conn.execute(f"INSERT INTO SLEEP_DATA (start, stop) VALUES ({timestamp}, {timestamp + 28800})")
            conn.commit()
            conn.close()
            
            # Test DatabaseManager with limit
            db_manager = DatabaseManager(tmp_path)
            results = db_manager.get_sleep_data(limit=5)
            
            # Should only get 5 records
            assert len(results) == 5
        finally:
            # Clean up
            tmp_path.unlink()
    
    def test_get_sleep_data_caps_limit_at_1000(self):
        """Test that get_sleep_data() caps limit at 1000."""
        # Create a temporary database file
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            tmp_path = Path(tmp.name)
        
        try:
            # Create a database with sleep data
            conn = sqlite3.connect(str(tmp_path))
            conn.execute("CREATE TABLE SLEEP_DATA (id INTEGER PRIMARY KEY, start INTEGER, stop INTEGER)")
            conn.execute("INSERT INTO SLEEP_DATA (start, stop) VALUES (1704142800, 1704171600)")
            conn.commit()
            conn.close()
            
            # Test DatabaseManager with limit > 1000
            db_manager = DatabaseManager(tmp_path)
            # This should not raise an error and should cap at 1000
            results = db_manager.get_sleep_data(limit=5000)
            
            # Should get the record (only 1 exists)
            assert len(results) == 1
        finally:
            # Clean up
            tmp_path.unlink()
    
    def test_get_heart_rate_data_returns_records(self):
        """Test that get_heart_rate_data() returns heart rate records."""
        # Create a temporary database file
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            tmp_path = Path(tmp.name)
        
        try:
            # Create a database with heart rate data
            conn = sqlite3.connect(str(tmp_path))
            conn.execute("CREATE TABLE HEART_RATE (id INTEGER PRIMARY KEY, date INTEGER, heart_rate INTEGER)")
            conn.execute("INSERT INTO HEART_RATE (date, heart_rate) VALUES (1704142800, 72)")
            conn.execute("INSERT INTO HEART_RATE (date, heart_rate) VALUES (1704229200, 68)")
            conn.commit()
            conn.close()
            
            # Test DatabaseManager
            db_manager = DatabaseManager(tmp_path)
            results = db_manager.get_heart_rate_data()
            
            # Verify results
            assert len(results) == 2
            assert 'date' in results[0]
            assert 'heart_rate' in results[0]
            # Timestamp should be converted
            assert isinstance(results[0]['date'], str)
        finally:
            # Clean up
            tmp_path.unlink()
    
    def test_get_heart_rate_data_with_filters(self):
        """Test that get_heart_rate_data() filters by date range and limit."""
        # Create a temporary database file
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            tmp_path = Path(tmp.name)
        
        try:
            # Create a database with heart rate data
            conn = sqlite3.connect(str(tmp_path))
            conn.execute("CREATE TABLE HEART_RATE (id INTEGER PRIMARY KEY, date INTEGER, heart_rate INTEGER)")
            for i in range(10):
                timestamp = 1704142800 + (i * 86400)
                conn.execute(f"INSERT INTO HEART_RATE (date, heart_rate) VALUES ({timestamp}, {70 + i})")
            conn.commit()
            conn.close()
            
            # Test DatabaseManager with filters
            db_manager = DatabaseManager(tmp_path)
            results = db_manager.get_heart_rate_data(start_date='2024-01-03', limit=3)
            
            # Should get at most 3 records from Jan 3 onwards
            assert len(results) <= 3
        finally:
            # Clean up
            tmp_path.unlink()
    
    def test_get_activity_data_returns_records(self):
        """Test that get_activity_data() returns activity records."""
        # Create a temporary database file
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            tmp_path = Path(tmp.name)
        
        try:
            # Create a database with activity data
            conn = sqlite3.connect(str(tmp_path))
            conn.execute("CREATE TABLE ACTIVITY_DATA (id INTEGER PRIMARY KEY, date INTEGER, steps INTEGER, calories REAL, distance REAL)")
            conn.execute("INSERT INTO ACTIVITY_DATA (date, steps, calories, distance) VALUES (1704142800, 8500, 320.5, 6200.0)")
            conn.execute("INSERT INTO ACTIVITY_DATA (date, steps, calories, distance) VALUES (1704229200, 10200, 385.2, 7500.0)")
            conn.commit()
            conn.close()
            
            # Test DatabaseManager
            db_manager = DatabaseManager(tmp_path)
            results = db_manager.get_activity_data()
            
            # Verify results
            assert len(results) == 2
            assert 'date' in results[0]
            assert 'steps' in results[0]
            assert 'calories' in results[0]
            assert 'distance' in results[0]
            # Timestamp should be converted
            assert isinstance(results[0]['date'], str)
        finally:
            # Clean up
            tmp_path.unlink()
    
    def test_get_activity_data_with_filters(self):
        """Test that get_activity_data() filters by date range and limit."""
        # Create a temporary database file
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            tmp_path = Path(tmp.name)
        
        try:
            # Create a database with activity data
            conn = sqlite3.connect(str(tmp_path))
            conn.execute("CREATE TABLE ACTIVITY_DATA (id INTEGER PRIMARY KEY, date INTEGER, steps INTEGER)")
            for i in range(10):
                timestamp = 1704142800 + (i * 86400)
                conn.execute(f"INSERT INTO ACTIVITY_DATA (date, steps) VALUES ({timestamp}, {8000 + i * 100})")
            conn.commit()
            conn.close()
            
            # Test DatabaseManager with filters
            db_manager = DatabaseManager(tmp_path)
            results = db_manager.get_activity_data(end_date='2024-01-05', limit=2)
            
            # Should get at most 2 records up to Jan 5
            assert len(results) <= 2
        finally:
            # Clean up
            tmp_path.unlink()
