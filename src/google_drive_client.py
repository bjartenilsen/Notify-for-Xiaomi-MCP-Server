"""
Google Drive client for Notify Xiaomi MCP Server.

This module provides OAuth2 authentication and file operations for Google Drive.
All error messages are in Norwegian as per requirements.
"""

import os
import pickle
from typing import Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from .config import CREDENTIALS_PATH, TOKEN_PATH
from .error_handling import get_error_message

# Google Drive API scopes - read-only access
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']


class GoogleDriveClient:
    """
    Client for Google Drive authentication and file operations.
    
    This client handles OAuth2 authentication with automatic token refresh
    and provides methods for finding folders and downloading files from
    Google Drive.
    
    Attributes:
        credentials_path: Path to credentials.json file
        token_path: Path to token.pickle file for storing OAuth2 tokens
        service: Google Drive API service instance (initialized after authentication)
        last_error: Last error message in Norwegian
    """
    
    def __init__(self, credentials_path: str = None, token_path: str = None):
        """
        Initialize GoogleDriveClient with paths to credentials and token files.
        
        Args:
            credentials_path: Path to credentials.json (defaults to config value)
            token_path: Path to token.pickle (defaults to config value)
        """
        self.credentials_path = credentials_path or str(CREDENTIALS_PATH)
        self.token_path = token_path or str(TOKEN_PATH)
        self.service = None
        self.last_error = ""
    
    def authenticate(self) -> bool:
        """
        Authenticate with Google Drive using OAuth2 flow.
        
        This method:
        1. Loads existing token from token.pickle if available
        2. Refreshes expired tokens automatically using refresh token
        3. Initiates OAuth2 flow for first-time authentication
        4. Saves new/refreshed tokens to token.pickle
        
        Returns:
            True if authentication succeeded, False otherwise
        
        Side Effects:
            - Sets self.service to authenticated Google Drive API service
            - Sets self.last_error to Norwegian error message on failure
            - Creates/updates token.pickle file on successful authentication
        
        Requirements:
            - 1.1: Initiate OAuth2 authentication using credentials.json
            - 1.2: Store OAuth2 token in token.pickle
            - 1.3: Reuse existing token without prompting
            - 1.4: Refresh expired tokens automatically
            - 1.5: Return Norwegian error messages for failures
        """
        creds = None
        
        # Check if credentials.json exists
        if not os.path.exists(self.credentials_path):
            self.last_error = get_error_message(
                "auth_no_credentials",
                path=self.credentials_path
            )
            return False
        
        # Load existing token from token.pickle if available
        if os.path.exists(self.token_path):
            try:
                with open(self.token_path, 'rb') as token:
                    creds = pickle.load(token)
            except Exception as e:
                self.last_error = get_error_message(
                    "auth_token_load_failed",
                    error=str(e)
                )
                return False
        
        # Refresh or create new token if needed
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                # Token is expired but has refresh token - refresh it
                try:
                    creds.refresh(Request())
                except Exception as e:
                    self.last_error = get_error_message(
                        "auth_token_refresh_failed",
                        error=str(e)
                    )
                    return False
            else:
                # No valid token - initiate OAuth2 flow
                try:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_path, 
                        SCOPES
                    )
                    creds = flow.run_local_server(port=0)
                except Exception as e:
                    self.last_error = get_error_message(
                        "auth_failed",
                        error=str(e)
                    )
                    return False
            
            # Save the new/refreshed token
            try:
                with open(self.token_path, 'wb') as token:
                    pickle.dump(creds, token)
            except Exception as e:
                self.last_error = get_error_message(
                    "auth_token_save_failed",
                    error=str(e)
                )
                return False
        
        # Build Google Drive API service
        try:
            self.service = build('drive', 'v3', credentials=creds)
            self.last_error = ""
            return True
        except Exception as e:
            self.last_error = get_error_message(
                "auth_service_creation_failed",
                error=str(e)
            )
            return False
    
    def find_folder(self, folder_name: str) -> Optional[str]:
        """
        Find a folder in Google Drive by name.
        
        This method searches for a folder with the exact name specified.
        If multiple folders with the same name exist, returns the first match.
        
        Args:
            folder_name: Name of the folder to search for
        
        Returns:
            Folder ID if found, None otherwise
        
        Side Effects:
            - Sets self.last_error to Norwegian error message if search fails
        
        Requirements:
            - 2.1: Locate folder named "Notify for xiaomi" in Google Drive
        """
        if not self.service:
            self.last_error = get_error_message("auth_service_not_initialized")
            return None
        
        try:
            # Search for folder by name
            # Query: name matches exactly AND mimeType is folder AND not trashed
            query = (
                f"name = '{folder_name}' and "
                "mimeType = 'application/vnd.google-apps.folder' and "
                "trashed = false"
            )
            
            results = self.service.files().list(
                q=query,
                spaces='drive',
                fields='files(id, name)',
                pageSize=1  # We only need the first match
            ).execute()
            
            files = results.get('files', [])
            
            if not files:
                self.last_error = get_error_message(
                    "folder_not_found",
                    folder_name=folder_name
                )
                return None
            
            # Return the ID of the first matching folder
            folder_id = files[0]['id']
            self.last_error = ""
            return folder_id
            
        except HttpError as e:
            self.last_error = get_error_message(
                "drive_search_failed",
                error=str(e)
            )
            return None
        except Exception as e:
            self.last_error = get_error_message(
                "drive_search_unexpected",
                error=str(e)
            )
            return None

    def download_file(self, folder_id: str, filename: str, destination: str) -> tuple[bool, int]:
        """
        Download a file from a Google Drive folder to a local destination.

        This method searches for a file with the specified name in the given folder
        and downloads it to the destination path. If a file already exists at the
        destination, it will be overwritten.

        Args:
            folder_id: ID of the folder containing the file
            filename: Name of the file to download
            destination: Local path where the file should be saved

        Returns:
            Tuple of (success: bool, file_size: int)
            - success: True if download succeeded, False otherwise
            - file_size: Size of downloaded file in bytes (0 on failure)

        Side Effects:
            - Creates/overwrites file at destination path
            - Sets self.last_error to Norwegian error message on failure

        Requirements:
            - 2.2: Download file named "backup.db" to local directory
            - 2.3: Overwrite existing file if present
            - 2.4: Return Norwegian error messages for failures
        """
        if not self.service:
            self.last_error = get_error_message("auth_service_not_initialized")
            return False, 0

        try:
            # Search for file by name in the specified folder
            query = (
                f"name = '{filename}' and "
                f"'{folder_id}' in parents and "
                "trashed = false"
            )

            results = self.service.files().list(
                q=query,
                spaces='drive',
                fields='files(id, name, size)',
                pageSize=1  # We only need the first match
            ).execute()

            files = results.get('files', [])

            if not files:
                self.last_error = get_error_message(
                    "file_not_found",
                    filename=filename
                )
                return False, 0

            file_id = files[0]['id']
            file_size = int(files[0].get('size', 0))

            # Download the file content
            from googleapiclient.http import MediaIoBaseDownload
            import io

            request = self.service.files().get_media(fileId=file_id)
            file_handle = io.BytesIO()
            downloader = MediaIoBaseDownload(file_handle, request)

            done = False
            while not done:
                status, done = downloader.next_chunk()

            # Write to destination file (overwrite if exists)
            try:
                with open(destination, 'wb') as f:
                    f.write(file_handle.getvalue())
            except Exception as e:
                self.last_error = get_error_message(
                    "file_write_failed",
                    path=destination,
                    error=str(e)
                )
                return False, 0

            self.last_error = ""
            return True, file_size

        except HttpError as e:
            self.last_error = get_error_message(
                "drive_download_failed",
                error=str(e)
            )
            return False, 0
        except Exception as e:
            self.last_error = get_error_message(
                "drive_download_unexpected",
                error=str(e)
            )
            return False, 0
    
    def get_last_error(self) -> str:
        """
        Get the last error message in Norwegian.
        
        Returns:
            Last error message, or empty string if no error
        """
        return self.last_error



