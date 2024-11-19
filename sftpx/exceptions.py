class AsyncSFTPError(Exception):
    """Base exception class for AsyncSFTP."""
    pass

class ConnectionError(AsyncSFTPError):
    """Raised when connection to SFTP server fails."""
    pass

class AuthenticationError(AsyncSFTPError):
    """Raised when authentication fails."""
    pass

class FileTransferError(AsyncSFTPError):
    """Raised when file transfer operations fail."""
    pass

class PermissionError(AsyncSFTPError):
    """Raised when operation fails due to insufficient permissions."""
    pass 