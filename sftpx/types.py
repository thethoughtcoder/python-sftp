from typing import Protocol, Callable, Union, Optional
from pathlib import Path
import os

PathLike = Union[str, Path, os.PathLike]
ProgressCallback = Callable[[int, int], None] 