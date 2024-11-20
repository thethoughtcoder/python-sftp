import os
from pathlib import Path
from typing import List
import asyncio
from functools import partial

async def ensure_async(func, *args, **kwargs):
    """Execute synchronous function in thread pool."""
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, partial(func, *args, **kwargs))

def normalize_path(path: Path) -> str:
    """Convert Path object to posix-style string path."""
    # Convert the path string to use forward slashes, regardless of platform
    return str(path).replace('\\', '/')

async def get_files_recursive(path: Path) -> List[Path]:
    """Get all files in directory recursively."""
    if not path.exists():
        raise FileNotFoundError(f"Path does not exist: {path}")
        
    files = []
    try:
        for item in path.rglob('*'):
            if item.is_file():
                files.append(item)
    except Exception as e:
        raise FileNotFoundError(f"Error accessing path: {path}") from e
        
    return files 