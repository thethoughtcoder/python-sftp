import pytest
import asyncio
from pathlib import Path
import os
import tempfile
import shutil

from sftpx.utils import ensure_async, normalize_path, get_files_recursive

@pytest.fixture
def temp_directory():
    """Create a temporary directory with some test files."""
    temp_dir = Path(tempfile.mkdtemp())
    
    # Create test directory structure
    (temp_dir / "dir1").mkdir()
    (temp_dir / "dir1" / "subdir").mkdir()
    
    # Create test files
    (temp_dir / "file1.txt").write_text("test1")
    (temp_dir / "dir1" / "file2.txt").write_text("test2")
    (temp_dir / "dir1" / "subdir" / "file3.txt").write_text("test3")
    
    yield temp_dir
    
    # Cleanup
    shutil.rmtree(temp_dir)

def test_normalize_path():
    """Test path normalization."""
    # Test Windows-style path
    path = Path("folder\\subfolder\\file.txt")
    assert normalize_path(path) == "folder/subfolder/file.txt"
    
    # Test Posix-style path
    path = Path("folder/subfolder/file.txt")
    assert normalize_path(path) == "folder/subfolder/file.txt"
    
    # Test root path
    path = Path("/")
    assert normalize_path(path) == "/"
    
    # Test current directory
    path = Path(".")
    assert normalize_path(path) == "."

@pytest.mark.asyncio
async def test_ensure_async():
    """Test ensure_async function."""
    def sync_func(x):
        return x * 2
    
    # Test with simple synchronous function
    result = await ensure_async(sync_func, 5)
    assert result == 10
    
    # Test with function that takes multiple arguments
    def sync_func_multi(x, y, z=1):
        return x + y + z
    
    result = await ensure_async(sync_func_multi, 1, 2, z=3)
    assert result == 6
    
    # Test with function that raises an exception
    def sync_func_error():
        raise ValueError("Test error")
    
    with pytest.raises(ValueError):
        await ensure_async(sync_func_error)

@pytest.mark.asyncio
async def test_get_files_recursive(temp_directory):
    """Test recursive file listing."""
    breakpoint()  # Debugger will pause here
    files = await get_files_recursive(temp_directory)
    
    # Convert to set of relative paths for easier comparison
    relative_paths = {str(f.relative_to(temp_directory)) for f in files}
    
    # Expected files
    expected_files = {
        "file1.txt",
        os.path.join("dir1", "file2.txt"),
        os.path.join("dir1", "subdir", "file3.txt")
    }
    
    assert relative_paths == expected_files
    
    # Test with empty directory
    empty_dir = temp_directory / "empty"
    empty_dir.mkdir()
    
    files = await get_files_recursive(empty_dir)
    assert len(files) == 0
    
    # Test with single file
    single_file = temp_directory / "single.txt"
    single_file.write_text("test")
    
    files = await get_files_recursive(single_file.parent)
    assert single_file in files

@pytest.mark.asyncio
async def test_get_files_recursive_error():
    """Test get_files_recursive with non-existent directory."""
    non_existent = Path("/non/existent/path")
    
    with pytest.raises(FileNotFoundError):
        await get_files_recursive(non_existent)

@pytest.mark.asyncio
async def test_ensure_async_concurrent():
    """Test ensure_async with concurrent execution."""
    async def slow_operation(delay, value):
        await asyncio.sleep(delay)
        return value
    
    # Run multiple operations concurrently
    tasks = [
        ensure_async(asyncio.sleep, 0.1),
        ensure_async(asyncio.sleep, 0.1),
        ensure_async(asyncio.sleep, 0.1)
    ]
    
    # Measure time to complete all tasks
    start_time = asyncio.get_event_loop().time()
    await asyncio.gather(*tasks)
    elapsed_time = asyncio.get_event_loop().time() - start_time
    
    # Should complete in roughly 0.1 seconds, not 0.3
    assert elapsed_time < 0.2  # Allow some margin for execution overhead 