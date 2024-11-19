import os
from pathlib import Path
from typing import List
import asyncio
from concurrent.futures import ThreadPoolExecutor

async def ensure_async(func, *args, **kwargs):
    """Execute synchronous function in thread pool."""
    loop = asyncio.get_running_loop()
    with ThreadPoolExecutor() as pool:
        return await loop.run_in_executor(pool, func, *args, **kwargs)

def normalize_path(path: Path) -> str:
    """Convert Path object to posix-style string path."""
    return str(path).replace(os.sep, '/')

async def get_files_recursive(path: Path) -> List[Path]:
    """Get all files in directory recursively."""
    files = []
    for item in path.rglob('*'):
        if item.is_file():
            files.append(item)
    return files 