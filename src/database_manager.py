"""
Database manager for read-only access to the Notify Xiaomi backup database.

This module provides the DatabaseManager class that handles all database operations
with read-only connections to ensure data integrity.
"""

import sqlite3
from pathlib import Path
from typing import Optional


class DatabaseManager:
    """
    Manages read-only access to the SQLite backup database.
    
    All database operations use read-only connections to prevent accidental
    modifications to the backup data.
    """
    
    def __init__(self, db_path: Path):
        """
        Initialize DatabaseManager with path to backup.db.
        
        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = db_path
    
    def get_readonly_connection(self) -> sqlite3.Connection:
        """
        Open database in read-only mode with dict-like row access.
        
        Uses URI connection string with ?mode=ro parameter to ensure
        read-only access. Sets row_factory to sqlite3.Row for dict-like
        access to query results.
        
        Returns:
            sqlite3.Connection: Read-only database connection
            
        Raises:
            sqlite3.OperationalError: If database file doesn't exist or can't be opened
        
        Requirements: 9.1, 9.3
        """
        # Create URI with read-only mode parameter
        uri = f"file:{self.db_path}?mode=ro"
        
        # Open connection with URI mode enabled
        conn = sqlite3.connect(uri, uri=True)
        
        # Set row_factory for dict-like access to rows
        conn.row_factory = sqlite3.Row
        
        return conn


    def exists(self) -> bool:
        """
        Check if database file exists at configured path.

        Returns:
            bool: True if database file exists, False otherwise

        Requirements: 3.5
        """
        return self.db_path.exists()

    def get_tables(self) -> list[dict]:
        """
        Return list of tables with columns and row counts.

        Queries sqlite_master for all table names, then for each table:
        - Gets column names and types from PRAGMA table_info
        - Counts total rows

        Returns:
            List of dicts with structure:
            [
                {
                    "name": str,
                    "columns": [{"name": str, "type": str}, ...],
                    "row_count": int
                },
                ...
            ]

        Raises:
            sqlite3.Error: If database read fails

        Requirements: 3.1, 3.2, 3.3, 3.4
        """
        conn = self.get_readonly_connection()
        try:
            cursor = conn.cursor()

            # Get all table names from sqlite_master
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
            )
            table_names = [row['name'] for row in cursor.fetchall()]

            tables = []
            for table_name in table_names:
                # Get column information using PRAGMA
                cursor.execute(f"PRAGMA table_info({table_name})")
                columns = [
                    {"name": row['name'], "type": row['type']}
                    for row in cursor.fetchall()
                ]

                # Count rows in table
                cursor.execute(f"SELECT COUNT(*) as count FROM {table_name}")
                row_count = cursor.fetchone()['count']

                tables.append({
                    "name": table_name,
                    "columns": columns,
                    "row_count": row_count
                })

            return tables
        finally:
            conn.close()

    def execute_query(self, sql: str, params: Optional[dict] = None) -> list[dict]:
        """
        Execute SELECT query with optional parameters.

        Args:
            sql: SQL SELECT statement to execute
            params: Optional dictionary of named parameters for the query

        Returns:
            List of dicts representing query results

        Raises:
            sqlite3.Error: If query execution fails

        Requirements: 7.3, 7.4, 7.5
        """
        conn = self.get_readonly_connection()
        try:
            cursor = conn.cursor()

            if params:
                cursor.execute(sql, params)
            else:
                cursor.execute(sql)

            # Convert Row objects to dicts
            columns = [desc[0] for desc in cursor.description]
            results = []
            for row in cursor.fetchall():
                results.append(dict(zip(columns, row)))

            return results
        finally:
            conn.close()

    def get_sleep_data(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: int = 100
    ) -> list[dict]:
        """
        Query sleep data with filters and convert timestamps.

        Args:
            start_date: Optional start date in YYYY-MM-DD format
            end_date: Optional end date in YYYY-MM-DD format
            limit: Maximum number of records (default 100, max 1000)

        Returns:
            List of sleep records with readable timestamps

        Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7, 4.8
        """
        from src.utils import TimestampConverter
        from datetime import datetime

        # Cap limit at 1000
        limit = min(limit, 1000)

        # Build query with filters
        query = "SELECT * FROM SLEEP_DATA"
        conditions = []
        params = {}

        if start_date:
            # Convert date to Unix timestamp (start of day)
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            start_timestamp = int(start_dt.timestamp())
            conditions.append("start >= :start_timestamp")
            params['start_timestamp'] = start_timestamp

        if end_date:
            # Convert date to Unix timestamp (end of day)
            end_dt = datetime.strptime(end_date, '%Y-%m-%d')
            end_timestamp = int(end_dt.timestamp()) + 86399  # End of day
            conditions.append("start <= :end_timestamp")
            params['end_timestamp'] = end_timestamp

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        query += " ORDER BY start DESC LIMIT :limit"
        params['limit'] = limit

        # Execute query
        results = self.execute_query(query, params)

        # Convert timestamps in results
        for record in results:
            if 'start' in record and record['start'] is not None:
                record['start'] = TimestampConverter.convert(record['start'])
            if 'stop' in record and record['stop'] is not None:
                record['stop'] = TimestampConverter.convert(record['stop'])

        return results

    def get_heart_rate_data(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: int = 100
    ) -> list[dict]:
        """
        Query heart rate data with filters and convert timestamps.

        Args:
            start_date: Optional start date in YYYY-MM-DD format
            end_date: Optional end date in YYYY-MM-DD format
            limit: Maximum number of records (default 100, max 1000)

        Returns:
            List of heart rate records with BPM and readable timestamps

        Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7, 5.8
        """
        from src.utils import TimestampConverter
        from datetime import datetime

        # Cap limit at 1000
        limit = min(limit, 1000)

        # Build query with filters
        query = "SELECT * FROM HEART_RATE"
        conditions = []
        params = {}

        if start_date:
            # Convert date to Unix timestamp (start of day)
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            start_timestamp = int(start_dt.timestamp())
            conditions.append("date >= :start_timestamp")
            params['start_timestamp'] = start_timestamp

        if end_date:
            # Convert date to Unix timestamp (end of day)
            end_dt = datetime.strptime(end_date, '%Y-%m-%d')
            end_timestamp = int(end_dt.timestamp()) + 86399  # End of day
            conditions.append("date <= :end_timestamp")
            params['end_timestamp'] = end_timestamp

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        query += " ORDER BY date DESC LIMIT :limit"
        params['limit'] = limit

        # Execute query
        results = self.execute_query(query, params)

        # Convert timestamps in results
        for record in results:
            if 'date' in record and record['date'] is not None:
                record['date'] = TimestampConverter.convert(record['date'])

        return results

    def get_activity_data(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: int = 100
    ) -> list[dict]:
        """
        Query activity data with filters and convert timestamps.

        Includes steps, calories, and distance fields in results.

        Args:
            start_date: Optional start date in YYYY-MM-DD format
            end_date: Optional end date in YYYY-MM-DD format
            limit: Maximum number of records (default 100, max 1000)

        Returns:
            List of activity records with readable timestamps

        Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7, 6.8, 6.9
        """
        from src.utils import TimestampConverter
        from datetime import datetime

        # Cap limit at 1000
        limit = min(limit, 1000)

        # Build query with filters
        query = "SELECT * FROM ACTIVITY_DATA"
        conditions = []
        params = {}

        if start_date:
            # Convert date to Unix timestamp (start of day)
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            start_timestamp = int(start_dt.timestamp())
            conditions.append("date >= :start_timestamp")
            params['start_timestamp'] = start_timestamp

        if end_date:
            # Convert date to Unix timestamp (end of day)
            end_dt = datetime.strptime(end_date, '%Y-%m-%d')
            end_timestamp = int(end_dt.timestamp()) + 86399  # End of day
            conditions.append("date <= :end_timestamp")
            params['end_timestamp'] = end_timestamp

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        query += " ORDER BY date DESC LIMIT :limit"
        params['limit'] = limit

        # Execute query
        results = self.execute_query(query, params)

        # Convert timestamps in results
        for record in results:
            if 'date' in record and record['date'] is not None:
                record['date'] = TimestampConverter.convert(record['date'])

        return results

