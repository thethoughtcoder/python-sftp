import pytest
import os
from pathlib import Path
import tempfile
from sftpx.client import AsyncSFTP
from sftpx.exceptions import FileTransferError

# Add skip marker that checks for environment variable
skip_sftp_tests = pytest.mark.skipif(
    'SFTP_TESTS' not in os.environ,
    reason="SFTP tests are disabled without SFTP_TESTS environment variable"
)

@pytest.fixture
async def sftp_client(sftp_credentials):
    """Create an SFTP client fixture."""
    client = AsyncSFTP(**sftp_credentials)
    await client.connect()
    yield client
    await client.close()

@pytest.fixture
def temp_file():
    """Create a temporary test file."""
    fd, path = tempfile.mkstemp()
    with os.fdopen(fd, 'w') as f:
        f.write('test content')
    yield path
    if os.path.exists(path):
        os.remove(path)

@pytest.mark.asyncio
@skip_sftp_tests
async def test_put_file(sftp_client, temp_file):
    """Test uploading a file to SFTP server."""
    remote_path = '/familyshared/test/uploaded_file.txt'
    
    try:
        # Test file upload
        await sftp_client.put(temp_file, remote_path)
        
        # Verify file exists on remote
        assert await sftp_client.exists(remote_path)
        
        # Verify file size
        stats = await sftp_client.stat(remote_path)
        assert stats.st_size > 0
        
        # Test progress callback
        progress_data = {'bytes_transferred': 0}
        
        def progress_callback(bytes_transferred, total_bytes):
            progress_data['bytes_transferred'] = bytes_transferred
        
        # Upload again with progress callback
        await sftp_client.put(temp_file, remote_path, callback=progress_callback)
        assert progress_data['bytes_transferred'] > 0
        
    finally:
        # Cleanup remote file
        if await sftp_client.exists(remote_path):
            await sftp_client.remove(remote_path)

@pytest.mark.asyncio
@skip_sftp_tests
async def test_put_nonexistent_file(sftp_client):
    """Test uploading a non-existent file."""
    local_path = '/nonexistent/path/file.txt'
    remote_path = '/familyshared/test/should_not_exist.txt'
    
    with pytest.raises(FileNotFoundError):
        await sftp_client.put(local_path, remote_path)

@pytest.mark.asyncio
@skip_sftp_tests
async def test_put_to_invalid_directory(sftp_client, temp_file):
    """Test uploading to a directory without write permissions."""
    remote_path = '/root/test_file.txt'  # Assuming no write permission to /root
    
    with pytest.raises(FileTransferError):
        await sftp_client.put(temp_file, remote_path)

@pytest.mark.asyncio
@skip_sftp_tests
async def test_get_file(sftp_client):
    """Test downloading a file from SFTP server."""
    # Test parameters
    remote_path = '/familyshared/test/f1.txt'
    local_path = '/tmp/f1.txt'
    
    try:
        # Ensure local file doesn't exist before test
        if os.path.exists(local_path):
            os.remove(local_path)
        
        # Test file download
        await sftp_client.get(remote_path, local_path)
        
        # Verify file was downloaded
        assert os.path.exists(local_path)
        assert os.path.getsize(local_path) > 0
        
        # Test progress callback
        progress_data = {'bytes_transferred': 0}
        
        def progress_callback(bytes_transferred, total_bytes):
            progress_data['bytes_transferred'] = bytes_transferred
        
        # Download again with progress callback
        await sftp_client.get(remote_path, local_path, callback=progress_callback)
        assert progress_data['bytes_transferred'] > 0
        
    finally:
        # Cleanup
        if os.path.exists(local_path):
            os.remove(local_path)

@pytest.mark.asyncio
@skip_sftp_tests
async def test_get_nonexistent_file(sftp_client):
    """Test downloading a non-existent file."""
    remote_path = '/familyshared/test/nonexistent.txt'
    local_path = '/tmp/nonexistent.txt'
    
    with pytest.raises(FileTransferError):
        await sftp_client.get(remote_path, local_path) 