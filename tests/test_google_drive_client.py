"""
Unit tests for GoogleDriveClient class.

These tests verify OAuth2 authentication, token persistence, and error handling.
"""

import os
import pickle
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

import pytest

from src.google_drive_client import GoogleDriveClient


class TestGoogleDriveClient:
    """Test suite for GoogleDriveClient class."""
    
    def test_init_with_default_paths(self):
        """Test that client initializes with default config paths."""
        client = GoogleDriveClient()
        
        assert client.credentials_path is not None
        assert client.token_path is not None
        assert client.service is None
        assert client.last_error == ""
    
    def test_init_with_custom_paths(self):
        """Test that client initializes with custom paths."""
        creds_path = "/custom/credentials.json"
        token_path = "/custom/token.pickle"
        
        client = GoogleDriveClient(
            credentials_path=creds_path,
            token_path=token_path
        )
        
        assert client.credentials_path == creds_path
        assert client.token_path == token_path
    
    def test_authenticate_missing_credentials(self):
        """Test authentication fails with Norwegian error when credentials.json is missing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            creds_path = os.path.join(tmpdir, "credentials.json")
            token_path = os.path.join(tmpdir, "token.pickle")
            
            client = GoogleDriveClient(
                credentials_path=creds_path,
                token_path=token_path
            )
            
            result = client.authenticate()
            
            assert result is False
            assert "Fant ikke credentials.json" in client.get_last_error()
            assert "credentials.json" in client.get_last_error()
    
    @patch('src.google_drive_client.pickle.dump')
    @patch('src.google_drive_client.build')
    @patch('src.google_drive_client.InstalledAppFlow')
    def test_authenticate_first_time_success(self, mock_flow_class, mock_build, mock_pickle_dump):
        """Test first-time OAuth2 authentication flow."""
        with tempfile.TemporaryDirectory() as tmpdir:
            creds_path = os.path.join(tmpdir, "credentials.json")
            token_path = os.path.join(tmpdir, "token.pickle")
            
            # Create dummy credentials.json
            Path(creds_path).write_text('{"installed": {}}')
            
            # Mock OAuth2 flow
            mock_creds = Mock()
            mock_creds.valid = True
            mock_creds.expired = False
            
            mock_flow = Mock()
            mock_flow.run_local_server.return_value = mock_creds
            mock_flow_class.from_client_secrets_file.return_value = mock_flow
            
            # Mock Google Drive service
            mock_service = Mock()
            mock_build.return_value = mock_service
            
            client = GoogleDriveClient(
                credentials_path=creds_path,
                token_path=token_path
            )
            
            result = client.authenticate()
            
            assert result is True
            assert client.service == mock_service
            assert client.get_last_error() == ""
            
            # Verify token was saved (pickle.dump was called)
            mock_pickle_dump.assert_called_once()
            
            # Verify OAuth2 flow was called
            mock_flow_class.from_client_secrets_file.assert_called_once()
            mock_flow.run_local_server.assert_called_once()
    
    @patch('src.google_drive_client.pickle.load')
    @patch('src.google_drive_client.build')
    def test_authenticate_with_existing_valid_token(self, mock_build, mock_pickle_load):
        """Test authentication reuses existing valid token without prompting."""
        with tempfile.TemporaryDirectory() as tmpdir:
            creds_path = os.path.join(tmpdir, "credentials.json")
            token_path = os.path.join(tmpdir, "token.pickle")
            
            # Create dummy credentials.json
            Path(creds_path).write_text('{"installed": {}}')
            
            # Create valid token
            mock_creds = Mock()
            mock_creds.valid = True
            mock_creds.expired = False
            
            # Create token file (content doesn't matter since we're mocking pickle.load)
            Path(token_path).write_bytes(b'dummy')
            
            # Mock pickle.load to return our mock credentials
            mock_pickle_load.return_value = mock_creds
            
            # Mock Google Drive service
            mock_service = Mock()
            mock_build.return_value = mock_service
            
            client = GoogleDriveClient(
                credentials_path=creds_path,
                token_path=token_path
            )
            
            result = client.authenticate()
            
            assert result is True
            assert client.service == mock_service
            assert client.get_last_error() == ""
    
    @patch('src.google_drive_client.pickle.dump')
    @patch('src.google_drive_client.pickle.load')
    @patch('src.google_drive_client.build')
    @patch('src.google_drive_client.Request')
    def test_authenticate_refresh_expired_token(self, mock_request_class, mock_build, mock_pickle_load, mock_pickle_dump):
        """Test authentication refreshes expired token automatically."""
        with tempfile.TemporaryDirectory() as tmpdir:
            creds_path = os.path.join(tmpdir, "credentials.json")
            token_path = os.path.join(tmpdir, "token.pickle")
            
            # Create dummy credentials.json
            Path(creds_path).write_text('{"installed": {}}')
            
            # Create expired token with refresh token
            mock_creds = Mock()
            mock_creds.valid = False
            mock_creds.expired = True
            mock_creds.refresh_token = "refresh_token_123"
            
            # After refresh, token becomes valid
            def refresh_side_effect(request):
                mock_creds.valid = True
                mock_creds.expired = False
            
            mock_creds.refresh = Mock(side_effect=refresh_side_effect)
            
            # Create token file and mock pickle.load
            Path(token_path).write_bytes(b'dummy')
            mock_pickle_load.return_value = mock_creds
            
            # Mock Google Drive service
            mock_service = Mock()
            mock_build.return_value = mock_service
            
            client = GoogleDriveClient(
                credentials_path=creds_path,
                token_path=token_path
            )
            
            result = client.authenticate()
            
            assert result is True
            assert client.service == mock_service
            assert client.get_last_error() == ""
            
            # Verify refresh was called
            mock_creds.refresh.assert_called_once()
            
            # Verify token was saved after refresh
            mock_pickle_dump.assert_called_once()
    
    @patch('src.google_drive_client.pickle.load')
    @patch('src.google_drive_client.Request')
    def test_authenticate_refresh_failure_norwegian_error(self, mock_request_class, mock_pickle_load):
        """Test authentication returns Norwegian error when token refresh fails."""
        with tempfile.TemporaryDirectory() as tmpdir:
            creds_path = os.path.join(tmpdir, "credentials.json")
            token_path = os.path.join(tmpdir, "token.pickle")
            
            # Create dummy credentials.json
            Path(creds_path).write_text('{"installed": {}}')
            
            # Create expired token with refresh token
            mock_creds = Mock()
            mock_creds.valid = False
            mock_creds.expired = True
            mock_creds.refresh_token = "refresh_token_123"
            mock_creds.refresh = Mock(side_effect=Exception("Refresh failed"))
            
            # Create token file and mock pickle.load
            Path(token_path).write_bytes(b'dummy')
            mock_pickle_load.return_value = mock_creds
            
            client = GoogleDriveClient(
                credentials_path=creds_path,
                token_path=token_path
            )
            
            result = client.authenticate()
            
            assert result is False
            error = client.get_last_error()
            assert "Kunne ikke fornye tilgangstokenet" in error
            assert "token.pickle" in error
    
    @patch('src.google_drive_client.InstalledAppFlow')
    def test_authenticate_oauth_flow_failure_norwegian_error(self, mock_flow_class):
        """Test authentication returns Norwegian error when OAuth2 flow fails."""
        with tempfile.TemporaryDirectory() as tmpdir:
            creds_path = os.path.join(tmpdir, "credentials.json")
            token_path = os.path.join(tmpdir, "token.pickle")
            
            # Create dummy credentials.json
            Path(creds_path).write_text('{"installed": {}}')
            
            # Mock OAuth2 flow to fail
            mock_flow_class.from_client_secrets_file.side_effect = Exception("OAuth failed")
            
            client = GoogleDriveClient(
                credentials_path=creds_path,
                token_path=token_path
            )
            
            result = client.authenticate()
            
            assert result is False
            error = client.get_last_error()
            assert "Google Drive-autentisering feilet" in error
            assert "credentials.json" in error
    
    def test_get_last_error_returns_empty_string_initially(self):
        """Test get_last_error returns empty string when no error occurred."""
        client = GoogleDriveClient()
        
        assert client.get_last_error() == ""
    
    def test_find_folder_without_authentication(self):
        """Test find_folder returns None with Norwegian error when service is not initialized."""
        client = GoogleDriveClient()
        
        result = client.find_folder("Test Folder")
        
        assert result is None
        error = client.get_last_error()
        assert "Google Drive-tjenesten er ikke initialisert" in error
        assert "authenticate()" in error
    
    @patch('src.google_drive_client.build')
    @patch('src.google_drive_client.pickle.load')
    def test_find_folder_success(self, mock_pickle_load, mock_build):
        """Test find_folder returns folder ID when folder is found."""
        with tempfile.TemporaryDirectory() as tmpdir:
            creds_path = os.path.join(tmpdir, "credentials.json")
            token_path = os.path.join(tmpdir, "token.pickle")
            
            # Create dummy credentials.json
            Path(creds_path).write_text('{"installed": {}}')
            
            # Create valid token
            mock_creds = Mock()
            mock_creds.valid = True
            mock_creds.expired = False
            
            # Create token file
            Path(token_path).write_bytes(b'dummy')
            mock_pickle_load.return_value = mock_creds
            
            # Mock Google Drive service
            mock_service = Mock()
            mock_files = Mock()
            mock_list = Mock()
            
            # Mock the files().list().execute() chain
            mock_list.execute.return_value = {
                'files': [
                    {'id': 'folder_123', 'name': 'Notify for xiaomi'}
                ]
            }
            mock_files.list.return_value = mock_list
            mock_service.files.return_value = mock_files
            mock_build.return_value = mock_service
            
            client = GoogleDriveClient(
                credentials_path=creds_path,
                token_path=token_path
            )
            
            # Authenticate first
            client.authenticate()
            
            # Find folder
            result = client.find_folder("Notify for xiaomi")
            
            assert result == "folder_123"
            assert client.get_last_error() == ""
            
            # Verify the query was constructed correctly
            call_args = mock_files.list.call_args
            assert call_args is not None
            query = call_args[1]['q']
            assert "name = 'Notify for xiaomi'" in query
            assert "mimeType = 'application/vnd.google-apps.folder'" in query
            assert "trashed = false" in query
    
    @patch('src.google_drive_client.build')
    @patch('src.google_drive_client.pickle.load')
    def test_find_folder_not_found(self, mock_pickle_load, mock_build):
        """Test find_folder returns None with Norwegian error when folder is not found."""
        with tempfile.TemporaryDirectory() as tmpdir:
            creds_path = os.path.join(tmpdir, "credentials.json")
            token_path = os.path.join(tmpdir, "token.pickle")
            
            # Create dummy credentials.json
            Path(creds_path).write_text('{"installed": {}}')
            
            # Create valid token
            mock_creds = Mock()
            mock_creds.valid = True
            mock_creds.expired = False
            
            # Create token file
            Path(token_path).write_bytes(b'dummy')
            mock_pickle_load.return_value = mock_creds
            
            # Mock Google Drive service
            mock_service = Mock()
            mock_files = Mock()
            mock_list = Mock()
            
            # Mock empty results (folder not found)
            mock_list.execute.return_value = {'files': []}
            mock_files.list.return_value = mock_list
            mock_service.files.return_value = mock_files
            mock_build.return_value = mock_service
            
            client = GoogleDriveClient(
                credentials_path=creds_path,
                token_path=token_path
            )
            
            # Authenticate first
            client.authenticate()
            
            # Find folder
            result = client.find_folder("Nonexistent Folder")
            
            assert result is None
            error = client.get_last_error()
            assert "Fant ikke mappen" in error
            assert "Nonexistent Folder" in error
    
    @patch('src.google_drive_client.build')
    @patch('src.google_drive_client.pickle.load')
    def test_find_folder_http_error(self, mock_pickle_load, mock_build):
        """Test find_folder returns None with Norwegian error when HTTP error occurs."""
        with tempfile.TemporaryDirectory() as tmpdir:
            creds_path = os.path.join(tmpdir, "credentials.json")
            token_path = os.path.join(tmpdir, "token.pickle")
            
            # Create dummy credentials.json
            Path(creds_path).write_text('{"installed": {}}')
            
            # Create valid token
            mock_creds = Mock()
            mock_creds.valid = True
            mock_creds.expired = False
            
            # Create token file
            Path(token_path).write_bytes(b'dummy')
            mock_pickle_load.return_value = mock_creds
            
            # Mock Google Drive service
            mock_service = Mock()
            mock_files = Mock()
            mock_list = Mock()
            
            # Mock HTTP error
            from googleapiclient.errors import HttpError
            mock_response = Mock()
            mock_response.status = 403
            mock_list.execute.side_effect = HttpError(mock_response, b'Access denied')
            mock_files.list.return_value = mock_list
            mock_service.files.return_value = mock_files
            mock_build.return_value = mock_service
            
            client = GoogleDriveClient(
                credentials_path=creds_path,
                token_path=token_path
            )
            
            # Authenticate first
            client.authenticate()
            
            # Find folder
            result = client.find_folder("Test Folder")
            
            assert result is None
            error = client.get_last_error()
            assert "Feil ved søk i Google Drive" in error
            assert "tilgang" in error
    
    @patch('src.google_drive_client.build')
    @patch('src.google_drive_client.pickle.load')
    def test_find_folder_unexpected_error(self, mock_pickle_load, mock_build):
        """Test find_folder returns None with Norwegian error when unexpected error occurs."""
        with tempfile.TemporaryDirectory() as tmpdir:
            creds_path = os.path.join(tmpdir, "credentials.json")
            token_path = os.path.join(tmpdir, "token.pickle")
            
            # Create dummy credentials.json
            Path(creds_path).write_text('{"installed": {}}')
            
            # Create valid token
            mock_creds = Mock()
            mock_creds.valid = True
            mock_creds.expired = False
            
            # Create token file
            Path(token_path).write_bytes(b'dummy')
            mock_pickle_load.return_value = mock_creds
            
            # Mock Google Drive service
            mock_service = Mock()
            mock_files = Mock()
            mock_list = Mock()
            
            # Mock unexpected error
            mock_list.execute.side_effect = Exception("Network error")
            mock_files.list.return_value = mock_list
            mock_service.files.return_value = mock_files
            mock_build.return_value = mock_service
            
            client = GoogleDriveClient(
                credentials_path=creds_path,
                token_path=token_path
            )
            
            # Authenticate first
            client.authenticate()
            
            # Find folder
            result = client.find_folder("Test Folder")
            
            assert result is None
            error = client.get_last_error()
            assert "Uventet feil ved søk etter mappe" in error
    
    def test_download_file_without_authentication(self):
        """Test download_file returns failure with Norwegian error when service is not initialized."""
        client = GoogleDriveClient()
        
        success, file_size = client.download_file("folder_123", "backup.db", "/tmp/backup.db")
        
        assert success is False
        assert file_size == 0
        error = client.get_last_error()
        assert "Google Drive-tjenesten er ikke initialisert" in error
        assert "authenticate()" in error
    
    @patch('src.google_drive_client.build')
    @patch('src.google_drive_client.pickle.load')
    def test_download_file_success(self, mock_pickle_load, mock_build):
        """Test download_file successfully downloads file and returns size."""
        with tempfile.TemporaryDirectory() as tmpdir:
            creds_path = os.path.join(tmpdir, "credentials.json")
            token_path = os.path.join(tmpdir, "token.pickle")
            destination = os.path.join(tmpdir, "backup.db")
            
            # Create dummy credentials.json
            Path(creds_path).write_text('{"installed": {}}')
            
            # Create valid token
            mock_creds = Mock()
            mock_creds.valid = True
            mock_creds.expired = False
            
            # Create token file
            Path(token_path).write_bytes(b'dummy')
            mock_pickle_load.return_value = mock_creds
            
            # Mock Google Drive service
            mock_service = Mock()
            mock_files = Mock()
            mock_list = Mock()
            
            # Mock file search results
            mock_list.execute.return_value = {
                'files': [
                    {'id': 'file_456', 'name': 'backup.db', 'size': '1024'}
                ]
            }
            mock_files.list.return_value = mock_list
            
            # Mock file download
            mock_request = Mock()
            mock_files.get_media.return_value = mock_request
            
            # Mock MediaIoBaseDownload
            with patch('googleapiclient.http.MediaIoBaseDownload') as mock_downloader_class:
                mock_downloader = Mock()
                # Simulate download completion in one chunk
                mock_downloader.next_chunk.return_value = (Mock(progress=lambda: 1.0), True)
                mock_downloader_class.return_value = mock_downloader
                
                # Mock the file handle to return test data
                with patch('io.BytesIO') as mock_bytesio:
                    mock_file_handle = Mock()
                    mock_file_handle.getvalue.return_value = b'test database content'
                    mock_bytesio.return_value = mock_file_handle
                    
                    mock_service.files.return_value = mock_files
                    mock_build.return_value = mock_service
                    
                    client = GoogleDriveClient(
                        credentials_path=creds_path,
                        token_path=token_path
                    )
                    
                    # Authenticate first
                    client.authenticate()
                    
                    # Download file
                    success, file_size = client.download_file("folder_123", "backup.db", destination)
                    
                    assert success is True
                    assert file_size == 1024
                    assert client.get_last_error() == ""
                    
                    # Verify file was written
                    assert os.path.exists(destination)
                    with open(destination, 'rb') as f:
                        content = f.read()
                        assert content == b'test database content'
                    
                    # Verify the query was constructed correctly
                    call_args = mock_files.list.call_args
                    assert call_args is not None
                    query = call_args[1]['q']
                    assert "name = 'backup.db'" in query
                    assert "'folder_123' in parents" in query
                    assert "trashed = false" in query
    
    @patch('src.google_drive_client.build')
    @patch('src.google_drive_client.pickle.load')
    def test_download_file_overwrites_existing(self, mock_pickle_load, mock_build):
        """Test download_file overwrites existing file at destination."""
        with tempfile.TemporaryDirectory() as tmpdir:
            creds_path = os.path.join(tmpdir, "credentials.json")
            token_path = os.path.join(tmpdir, "token.pickle")
            destination = os.path.join(tmpdir, "backup.db")
            
            # Create existing file with old content
            Path(destination).write_bytes(b'old content')
            
            # Create dummy credentials.json
            Path(creds_path).write_text('{"installed": {}}')
            
            # Create valid token
            mock_creds = Mock()
            mock_creds.valid = True
            mock_creds.expired = False
            
            # Create token file
            Path(token_path).write_bytes(b'dummy')
            mock_pickle_load.return_value = mock_creds
            
            # Mock Google Drive service
            mock_service = Mock()
            mock_files = Mock()
            mock_list = Mock()
            
            # Mock file search results
            mock_list.execute.return_value = {
                'files': [
                    {'id': 'file_456', 'name': 'backup.db', 'size': '2048'}
                ]
            }
            mock_files.list.return_value = mock_list
            
            # Mock file download
            mock_request = Mock()
            mock_files.get_media.return_value = mock_request
            
            # Mock MediaIoBaseDownload
            with patch('googleapiclient.http.MediaIoBaseDownload') as mock_downloader_class:
                mock_downloader = Mock()
                mock_downloader.next_chunk.return_value = (Mock(progress=lambda: 1.0), True)
                mock_downloader_class.return_value = mock_downloader
                
                # Mock the file handle to return new data
                with patch('io.BytesIO') as mock_bytesio:
                    mock_file_handle = Mock()
                    mock_file_handle.getvalue.return_value = b'new database content'
                    mock_bytesio.return_value = mock_file_handle
                    
                    mock_service.files.return_value = mock_files
                    mock_build.return_value = mock_service
                    
                    client = GoogleDriveClient(
                        credentials_path=creds_path,
                        token_path=token_path
                    )
                    
                    # Authenticate first
                    client.authenticate()
                    
                    # Download file
                    success, file_size = client.download_file("folder_123", "backup.db", destination)
                    
                    assert success is True
                    assert file_size == 2048
                    
                    # Verify file was overwritten with new content
                    with open(destination, 'rb') as f:
                        content = f.read()
                        assert content == b'new database content'
                        assert content != b'old content'
    
    @patch('src.google_drive_client.build')
    @patch('src.google_drive_client.pickle.load')
    def test_download_file_not_found(self, mock_pickle_load, mock_build):
        """Test download_file returns failure with Norwegian error when file is not found."""
        with tempfile.TemporaryDirectory() as tmpdir:
            creds_path = os.path.join(tmpdir, "credentials.json")
            token_path = os.path.join(tmpdir, "token.pickle")
            destination = os.path.join(tmpdir, "backup.db")
            
            # Create dummy credentials.json
            Path(creds_path).write_text('{"installed": {}}')
            
            # Create valid token
            mock_creds = Mock()
            mock_creds.valid = True
            mock_creds.expired = False
            
            # Create token file
            Path(token_path).write_bytes(b'dummy')
            mock_pickle_load.return_value = mock_creds
            
            # Mock Google Drive service
            mock_service = Mock()
            mock_files = Mock()
            mock_list = Mock()
            
            # Mock empty results (file not found)
            mock_list.execute.return_value = {'files': []}
            mock_files.list.return_value = mock_list
            mock_service.files.return_value = mock_files
            mock_build.return_value = mock_service
            
            client = GoogleDriveClient(
                credentials_path=creds_path,
                token_path=token_path
            )
            
            # Authenticate first
            client.authenticate()
            
            # Download file
            success, file_size = client.download_file("folder_123", "backup.db", destination)
            
            assert success is False
            assert file_size == 0
            error = client.get_last_error()
            assert "Fant ikke filen" in error
            assert "backup.db" in error
    
    @patch('src.google_drive_client.build')
    @patch('src.google_drive_client.pickle.load')
    def test_download_file_http_error(self, mock_pickle_load, mock_build):
        """Test download_file returns failure with Norwegian error when HTTP error occurs."""
        with tempfile.TemporaryDirectory() as tmpdir:
            creds_path = os.path.join(tmpdir, "credentials.json")
            token_path = os.path.join(tmpdir, "token.pickle")
            destination = os.path.join(tmpdir, "backup.db")
            
            # Create dummy credentials.json
            Path(creds_path).write_text('{"installed": {}}')
            
            # Create valid token
            mock_creds = Mock()
            mock_creds.valid = True
            mock_creds.expired = False
            
            # Create token file
            Path(token_path).write_bytes(b'dummy')
            mock_pickle_load.return_value = mock_creds
            
            # Mock Google Drive service
            mock_service = Mock()
            mock_files = Mock()
            mock_list = Mock()
            
            # Mock HTTP error
            from googleapiclient.errors import HttpError
            mock_response = Mock()
            mock_response.status = 403
            mock_list.execute.side_effect = HttpError(mock_response, b'Access denied')
            mock_files.list.return_value = mock_list
            mock_service.files.return_value = mock_files
            mock_build.return_value = mock_service
            
            client = GoogleDriveClient(
                credentials_path=creds_path,
                token_path=token_path
            )
            
            # Authenticate first
            client.authenticate()
            
            # Download file
            success, file_size = client.download_file("folder_123", "backup.db", destination)
            
            assert success is False
            assert file_size == 0
            error = client.get_last_error()
            assert "Feil ved nedlasting fra Google Drive" in error
            assert "tilgang" in error
    
    @patch('src.google_drive_client.build')
    @patch('src.google_drive_client.pickle.load')
    def test_download_file_write_error(self, mock_pickle_load, mock_build):
        """Test download_file returns failure with Norwegian error when file write fails."""
        with tempfile.TemporaryDirectory() as tmpdir:
            creds_path = os.path.join(tmpdir, "credentials.json")
            token_path = os.path.join(tmpdir, "token.pickle")
            # Use invalid destination path (directory doesn't exist)
            destination = "/nonexistent/directory/backup.db"
            
            # Create dummy credentials.json
            Path(creds_path).write_text('{"installed": {}}')
            
            # Create valid token
            mock_creds = Mock()
            mock_creds.valid = True
            mock_creds.expired = False
            
            # Create token file
            Path(token_path).write_bytes(b'dummy')
            mock_pickle_load.return_value = mock_creds
            
            # Mock Google Drive service
            mock_service = Mock()
            mock_files = Mock()
            mock_list = Mock()
            
            # Mock file search results
            mock_list.execute.return_value = {
                'files': [
                    {'id': 'file_456', 'name': 'backup.db', 'size': '1024'}
                ]
            }
            mock_files.list.return_value = mock_list
            
            # Mock file download
            mock_request = Mock()
            mock_files.get_media.return_value = mock_request
            
            # Mock MediaIoBaseDownload
            with patch('googleapiclient.http.MediaIoBaseDownload') as mock_downloader_class:
                mock_downloader = Mock()
                mock_downloader.next_chunk.return_value = (Mock(progress=lambda: 1.0), True)
                mock_downloader_class.return_value = mock_downloader
                
                # Mock the file handle
                with patch('io.BytesIO') as mock_bytesio:
                    mock_file_handle = Mock()
                    mock_file_handle.getvalue.return_value = b'test content'
                    mock_bytesio.return_value = mock_file_handle
                    
                    mock_service.files.return_value = mock_files
                    mock_build.return_value = mock_service
                    
                    client = GoogleDriveClient(
                        credentials_path=creds_path,
                        token_path=token_path
                    )
                    
                    # Authenticate first
                    client.authenticate()
                    
                    # Download file (should fail due to invalid destination)
                    success, file_size = client.download_file("folder_123", "backup.db", destination)
                    
                    assert success is False
                    assert file_size == 0
                    error = client.get_last_error()
                    assert "Kunne ikke skrive til" in error
                    assert destination in error

