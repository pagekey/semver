"""Module related to config files."""
import os
from pathlib import Path


DEFAULT_CONFIG = "coming soon"


def load_config(config_path: Path) -> None:
    if not config_path.is_file():
        return DEFAULT_CONFIG
