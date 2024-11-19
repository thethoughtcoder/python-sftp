import asyncio
import paramiko
from pathlib import Path
from typing import Optional, List
import os

from .exceptions import (
    AsyncSFTPError,
    ConnectionError,
    AuthenticationError,
    FileTransferError,
    PermissionError,
)
from .types import PathLike, ProgressCallback
from .utils import ensure_async, normalize_path, get_files_recursive

class AsyncSFTP:
    def __init__(
        self,
        hostname: str,
        username: str,
        password: Optional[str] = None,
        private_key_path: Optional[PathLike] = None,
        port: int = 22,
        timeout: float = 30,
        max_retries: int = 3,
        retry_delay: float = 1.0,
    ):
        self.hostname = hostname
        self.username = username
        self.password = password
        self.private_key_path = private_key_path
        self.port = port
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        
        self._transport = None
        self._sftp = None
        self._client = None

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def connect(self):
        """Establish SFTP connection."""
        try:
            self._client = paramiko.SSHClient()
            self._client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            connect_kwargs = {
                'hostname': self.hostname,
                'username': self.username,
                'port': self.port,
                'timeout': self.timeout,
            }

            if self.password:
                connect_kwargs['password'] = self.password
            elif self.private_key_path:
                connect_kwargs['key_filename'] = str(self.private_key_path)

            await ensure_async(self._client.connect, **connect_kwargs)
            self._transport = self._client.get_transport()
            self._sftp = await ensure_async(paramiko.SFTPClient.from_transport, self._transport)

        except paramiko.AuthenticationException as e:
            raise AuthenticationError(f"Authentication failed: {str(e)}")
        except paramiko.SSHException as e:
            raise ConnectionError(f"SSH connection failed: {str(e)}")
        except Exception as e:
            raise AsyncSFTPError(f"Failed to establish SFTP connection: {str(e)}")

    async def close(self):
        """Close SFTP connection."""
        if self._sftp:
            await ensure_async(self._sftp.close)
        if self._client:
            self._client.close()

    async def put(
        self,
        local_path: PathLike,
        remote_path: PathLike,
        callback: Optional[ProgressCallback] = None
    ):
        """Upload a file to remote server."""
        local_path = Path(local_path)
        remote_path = normalize_path(Path(remote_path))

        if not local_path.exists():
            raise FileNotFoundError(f"Local file not found: {local_path}")

        try:
            await ensure_async(
                self._sftp.put,
                str(local_path),
                remote_path,
                callback=callback
            )
        except Exception as e:
            raise FileTransferError(f"Failed to upload file: {str(e)}")

    async def get(
        self,
        remote_path: PathLike,
        local_path: PathLike,
        callback: Optional[ProgressCallback] = None
    ):
        """Download a file from remote server."""
        local_path = Path(local_path)
        remote_path = normalize_path(Path(remote_path))

        try:
            await ensure_async(
                self._sftp.get,
                remote_path,
                str(local_path),
                callback=callback
            )
        except Exception as e:
            raise FileTransferError(f"Failed to download file: {str(e)}")

    async def listdir(self, path: PathLike = '.') -> List[str]:
        """List directory contents."""
        path = normalize_path(Path(path))
        try:
            return await ensure_async(self._sftp.listdir, path)
        except Exception as e:
            raise AsyncSFTPError(f"Failed to list directory: {str(e)}")

    async def mkdir(self, path: PathLike, mode: int = 511):
        """Create a directory."""
        path = normalize_path(Path(path))
        try:
            await ensure_async(self._sftp.mkdir, path, mode)
        except Exception as e:
            raise AsyncSFTPError(f"Failed to create directory: {str(e)}")

    async def rmdir(self, path: PathLike):
        """Remove a directory."""
        path = normalize_path(Path(path))
        try:
            await ensure_async(self._sftp.rmdir, path)
        except Exception as e:
            raise AsyncSFTPError(f"Failed to remove directory: {str(e)}")

    async def remove(self, path: PathLike):
        """Remove a file."""
        path = normalize_path(Path(path))
        try:
            await ensure_async(self._sftp.remove, path)
        except Exception as e:
            raise AsyncSFTPError(f"Failed to remove file: {str(e)}")

    async def exists(self, path: PathLike) -> bool:
        """Check if path exists."""
        path = normalize_path(Path(path))
        try:
            await ensure_async(self._sftp.stat, path)
            return True
        except FileNotFoundError:
            return False
        except Exception as e:
            raise AsyncSFTPError(f"Failed to check path existence: {str(e)}")

    async def stat(self, path: PathLike) -> paramiko.SFTPAttributes:
        """Get file attributes."""
        path = normalize_path(Path(path))
        try:
            return await ensure_async(self._sftp.stat, path)
        except Exception as e:
            raise AsyncSFTPError(f"Failed to get file attributes: {str(e)}")

    async def put_dir(
        self,
        local_path: PathLike,
        remote_path: PathLike,
        callback: Optional[ProgressCallback] = None
    ):
        """Upload a directory recursively."""
        local_path = Path(local_path)
        remote_base = Path(remote_path)

        if not local_path.is_dir():
            raise NotADirectoryError(f"Local path is not a directory: {local_path}")

        files = await get_files_recursive(local_path)
        for file in files:
            relative_path = file.relative_to(local_path)
            remote_file_path = remote_base / relative_path
            
            # Create parent directories if they don't exist
            await self.mkdir(remote_file_path.parent, mode=511)
            
            # Upload file
            await self.put(file, remote_file_path, callback)

    async def get_dir(
        self,
        remote_path: PathLike,
        local_path: PathLike,
        callback: Optional[ProgressCallback] = None
    ):
        """Download a directory recursively."""
        local_path = Path(local_path)
        remote_path = Path(remote_path)

        # Create local directory if it doesn't exist
        local_path.mkdir(parents=True, exist_ok=True)

        # List remote directory contents
        files = await self.listdir(remote_path)
        
        for item in files:
            remote_item = remote_path / item
            local_item = local_path / item

            try:
                # Check if item is a directory
                await self.stat(remote_item)
                if await ensure_async(self._sftp.isdir, str(remote_item)):
                    await self.get_dir(remote_item, local_item, callback)
                else:
                    await self.get(remote_item, local_item, callback)
            except Exception as e:
                raise FileTransferError(f"Failed to download directory: {str(e)}") 