# AsyncSFTP

A modern asynchronous SFTP client wrapper built on top of Paramiko using Python's asyncio. This library provides a simple, efficient, and non-blocking interface for SFTP operations.

## Features

- Asynchronous SFTP operations using asyncio
- Built on top of the reliable Paramiko library
- Non-blocking file transfers
- Support for common SFTP operations:
  - Upload files and directories
  - Download files and directories
  - List directory contents
  - Create/remove directories
  - Check file existence
  - Get file attributes
- Connection pooling
- Automatic retry mechanisms
- Progress tracking for file transfers

## Requirements

- Python 3.9+
- paramiko
- asyncio

## Installation 

## Quick Start

## API Reference

### AsyncSFTP Class

#### Constructor Parameters

- `hostname` (str): Remote host to connect to
- `username` (str): Username for authentication
- `password` (str, optional): Password for authentication
- `private_key_path` (str, optional): Path to private key file
- `port` (int, optional): Port number (default: 22)
- `timeout` (float, optional): Connection timeout in seconds
- `max_retries` (int, optional): Maximum number of retry attempts
- `retry_delay` (float, optional): Delay between retries in seconds

#### Methods

- `async with` context manager support
- `async put(local_path, remote_path, callback=None)`
- `async get(remote_path, local_path, callback=None)`
- `async listdir(path='.')`
- `async mkdir(path, mode=511)`
- `async rmdir(path)`
- `async remove(path)`
- `async exists(path)`
- `async stat(path)`
- `async put_dir(local_path, remote_path, callback=None)`
- `async get_dir(remote_path, local_path, callback=None)`

## Error Handling

The library provides custom exceptions for different error scenarios:

- `AsyncSFTPError`: Base exception class
- `ConnectionError`: Connection-related errors
- `AuthenticationError`: Authentication failures
- `FileTransferError`: File transfer issues
- `FileNotFoundError`: Remote file not found
- `PermissionError`: Insufficient permissions

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.