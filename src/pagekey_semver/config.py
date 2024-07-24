"""Module related to config files."""
import json
from pathlib import Path
from typing import List

from pydantic import BaseModel


DEFAULT_CONFIG_DICT = {
    "prefixes": ["something"],
}

class SemverConfig(BaseModel):
    prefixes: List[str]


def load_config(config_path: Path) -> None:
    if not config_path.is_file():
        return SemverConfig(**DEFAULT_CONFIG_DICT)
    with open(config_path, "r") as config_file:
        config_raw = config_file.read()
    config_dict = json.loads(config_raw)
    config_merged = {**DEFAULT_CONFIG_DICT, **config_dict}
    return SemverConfig(**config_merged)
