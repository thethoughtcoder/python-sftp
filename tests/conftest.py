import os
import pytest

@pytest.fixture(scope="session")
def sftp_credentials():
    return {
        'hostname': os.getenv('SFTP_HOST', 'testhost'),
        'username': os.getenv('SFTP_USER', 'testuser'),
        'password': os.getenv('SFTP_PASSWORD', 'testpassword'),
        'port': int(os.getenv('SFTP_PORT', '22'))
    } 