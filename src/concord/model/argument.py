from dataclasses import dataclass
from pathlib import Path


@dataclass
class Args:
    bot_name: str
    tool_directory_paths: list[Path]
    is_debug: bool
