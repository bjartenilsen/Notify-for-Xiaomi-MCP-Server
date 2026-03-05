"""
FastMCP server for Notify Xiaomi Health Data.

This module implements the MCP server with six tools for accessing health data
from the Notify for Xiaomi app backup database stored in Google Drive.

Tools:
- nxk_sync_database: Download backup database from Google Drive
- nxk_list_tables: List all tables with schema and row counts
- nxk_get_sleep: Retrieve sleep data with date filtering
- nxk_get_heart_rate: Retrieve heart rate measurements
- nxk_get_activity: Retrieve activity data (steps, calories, distance)
- nxk_query: Execute custom SELECT queries

Requirements: 10.1, 10.2, 10.3, 10.4
"""

import sys
from datetime import datetime
from typing import Optional

from fastmcp import FastMCP
from pydantic import ValidationError

from .config import (
    CREDENTIALS_PATH,
    TOKEN_PATH,
    DATABASE_PATH,
    DRIVE_FOLDER_NAME,
    DRIVE_FILE_NAME,
)
from .database_manager import DatabaseManager
from .google_drive_client import GoogleDriveClient
from .models import SleepParams, HeartRateParams, ActivityParams, QueryParams
from .error_handling import (
    get_error_message,
    create_error_response,
    create_success_response,
)


# Initialize FastMCP server
mcp = FastMCP(
    name="Notify Xiaomi Health Data",
    version="1.0.0"
)


# Initialize components
db_manager = DatabaseManager(DATABASE_PATH)
drive_client = GoogleDriveClient(str(CREDENTIALS_PATH), str(TOKEN_PATH))


@mcp.tool()
def nxk_sync_database() -> dict:
    """
    Synkroniser backup-databasen fra Google Drive.
    
    Laster ned den nyeste backup.db-filen fra "Notify for xiaomi"-mappen
    i Google Drive til lokal katalog (~/.notify-xiaomi-mcp/).
    
    Returns:
        Dict med status, melding, filstørrelse og tidsstempel
    
    Requirements: 2.1, 2.2, 2.3, 2.4, 2.5
    """
    try:
        # Authenticate with Google Drive
        if not drive_client.authenticate():
            return create_error_response(
                "auth",
                drive_client.get_last_error()
            )
        
        # Find the "Notify for xiaomi" folder
        folder_id = drive_client.find_folder(DRIVE_FOLDER_NAME)
        if not folder_id:
            return create_error_response(
                "resource",
                drive_client.get_last_error()
            )
        
        # Download backup.db file
        success, file_size = drive_client.download_file(
            folder_id,
            DRIVE_FILE_NAME,
            str(DATABASE_PATH)
        )
        
        if not success:
            return create_error_response(
                "execution",
                drive_client.get_last_error()
            )
        
        # Return success response with file info
        download_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
        
        return create_success_response({
            "message": f"Database synkronisert. Filstørrelse: {file_size} bytes.",
            "file_size_bytes": file_size,
            "download_timestamp": download_timestamp
        })
    
    except Exception as e:
        return create_error_response(
            "execution",
            get_error_message("sync_unexpected_error", error=str(e)),
            details=str(e)
        )


@mcp.tool()
def nxk_list_tables() -> dict:
    """
    List alle tabeller i databasen med struktur og antall rader.
    
    Viser tabellnavn, kolonner med datatyper, og totalt antall rader
    for hver tabell i backup-databasen.
    
    Returns:
        Dict med liste over tabeller og deres metadata
    
    Requirements: 3.1, 3.2, 3.3, 3.4, 3.5
    """
    try:
        # Check if database exists
        if not db_manager.exists():
            return create_error_response(
                "resource",
                get_error_message("db_not_found")
            )
        
        # Get table information
        tables = db_manager.get_tables()
        
        return create_success_response({
            "tables": tables
        })
    
    except Exception as e:
        return create_error_response(
            "execution",
            get_error_message("db_read_error", error=str(e)),
            details=str(e)
        )


@mcp.tool()
def nxk_get_sleep(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: Optional[int] = 100
) -> dict:
    """
    Hent søvndata med lesbare tidsstempler.
    
    Returnerer søvndata fra databasen med valgfri datofiltrering.
    Tidsstempler konverteres til YYYY-MM-DD HH:MM format.
    
    Args:
        start_date: Startdato i YYYY-MM-DD format (valgfri)
        end_date: Sluttdato i YYYY-MM-DD format (valgfri)
        limit: Maksimalt antall poster (1-1000, standard 100)
    
    Returns:
        Dict med søvnposter og antall
    
    Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7, 4.8
    """
    try:
        # Validate input parameters
        try:
            params = SleepParams(
                start_date=start_date,
                end_date=end_date,
                limit=limit
            )
        except ValidationError as e:
            # Extract first error message (already in Norwegian)
            error_msg = e.errors()[0]['msg']
            return create_error_response("validation", error_msg)
        
        # Check if database exists
        if not db_manager.exists():
            return create_error_response(
                "resource",
                get_error_message("db_not_found")
            )
        
        # Get sleep data
        records = db_manager.get_sleep_data(
            start_date=params.start_date,
            end_date=params.end_date,
            limit=params.limit
        )
        
        return create_success_response({
            "records": records,
            "count": len(records)
        })
    
    except Exception as e:
        return create_error_response(
            "execution",
            get_error_message("sleep_data_fetch_failed", error=str(e)),
            details=str(e)
        )


@mcp.tool()
def nxk_get_heart_rate(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: Optional[int] = 100
) -> dict:
    """
    Hent pulsmålinger med lesbare tidsstempler.
    
    Returnerer pulsdata fra databasen med valgfri datofiltrering.
    Tidsstempler konverteres til YYYY-MM-DD HH:MM format.
    
    Args:
        start_date: Startdato i YYYY-MM-DD format (valgfri)
        end_date: Sluttdato i YYYY-MM-DD format (valgfri)
        limit: Maksimalt antall poster (1-1000, standard 100)
    
    Returns:
        Dict med pulsmålinger og antall
    
    Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7, 5.8
    """
    try:
        # Validate input parameters
        try:
            params = HeartRateParams(
                start_date=start_date,
                end_date=end_date,
                limit=limit
            )
        except ValidationError as e:
            # Extract first error message (already in Norwegian)
            error_msg = e.errors()[0]['msg']
            return create_error_response("validation", error_msg)
        
        # Check if database exists
        if not db_manager.exists():
            return create_error_response(
                "resource",
                get_error_message("db_not_found")
            )
        
        # Get heart rate data
        records = db_manager.get_heart_rate_data(
            start_date=params.start_date,
            end_date=params.end_date,
            limit=params.limit
        )
        
        return create_success_response({
            "records": records,
            "count": len(records)
        })
    
    except Exception as e:
        return create_error_response(
            "execution",
            get_error_message("heart_rate_fetch_failed", error=str(e)),
            details=str(e)
        )


@mcp.tool()
def nxk_get_activity(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: Optional[int] = 100
) -> dict:
    """
    Hent aktivitetsdata inkludert skritt, kalorier og distanse.
    
    Returnerer aktivitetsdata fra databasen med valgfri datofiltrering.
    Tidsstempler konverteres til YYYY-MM-DD HH:MM format.
    
    Args:
        start_date: Startdato i YYYY-MM-DD format (valgfri)
        end_date: Sluttdato i YYYY-MM-DD format (valgfri)
        limit: Maksimalt antall poster (1-1000, standard 100)
    
    Returns:
        Dict med aktivitetsposter og antall
    
    Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7, 6.8, 6.9
    """
    try:
        # Validate input parameters
        try:
            params = ActivityParams(
                start_date=start_date,
                end_date=end_date,
                limit=limit
            )
        except ValidationError as e:
            # Extract first error message (already in Norwegian)
            error_msg = e.errors()[0]['msg']
            return create_error_response("validation", error_msg)
        
        # Check if database exists
        if not db_manager.exists():
            return create_error_response(
                "resource",
                get_error_message("db_not_found")
            )
        
        # Get activity data
        records = db_manager.get_activity_data(
            start_date=params.start_date,
            end_date=params.end_date,
            limit=params.limit
        )
        
        return create_success_response({
            "records": records,
            "count": len(records)
        })
    
    except Exception as e:
        return create_error_response(
            "execution",
            get_error_message("activity_data_fetch_failed", error=str(e)),
            details=str(e)
        )


@mcp.tool()
def nxk_query(sql: str) -> dict:
    """
    Utfør egendefinerte SELECT-spørringer mot databasen.
    
    Tillater kun SELECT-spørringer for å beskytte databasen mot
    skriveoperasjoner. Alle andre SQL-kommandoer avvises.
    
    Args:
        sql: SQL SELECT-spørring
    
    Returns:
        Dict med kolonner, rader og antall rader
    
    Requirements: 7.1, 7.2, 7.3, 7.4, 7.5
    """
    try:
        # Validate SQL query
        try:
            params = QueryParams(sql=sql)
        except ValidationError as e:
            # Extract first error message (already in Norwegian)
            error_msg = e.errors()[0]['msg']
            return create_error_response("validation", error_msg)
        
        # Check if database exists
        if not db_manager.exists():
            return create_error_response(
                "resource",
                get_error_message("db_not_found")
            )
        
        # Execute query
        results = db_manager.execute_query(params.sql)
        
        # Extract columns from first result if available
        columns = list(results[0].keys()) if results else []
        
        # Convert results to list of lists for rows
        rows = [list(record.values()) for record in results]
        
        return create_success_response({
            "columns": columns,
            "rows": rows,
            "row_count": len(rows)
        })
    
    except Exception as e:
        return create_error_response(
            "execution",
            get_error_message("query_execution_failed", error=str(e)),
            details=str(e)
        )


def main():
    """
    Main entry point for the MCP server.
    
    Runs the FastMCP server with stdio transport for Claude Desktop integration.
    Errors are logged to stderr as per requirements.
    """
    try:
        # Run server with stdio transport
        mcp.run(transport="stdio")
    except Exception as e:
        # Log errors to stderr
        print(f"Feil ved oppstart av MCP-server: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
