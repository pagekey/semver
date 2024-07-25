"""Module related to config files."""
import json
from pathlib import Path
from typing import List

from pydantic import BaseModel

from pagekey_semver.release import ReleaseType


class Prefix(BaseModel):
    label: str
    type: ReleaseType

class SemverConfig(BaseModel):
    prefixes: List[Prefix]

DEFAULT_CONFIG = SemverConfig(
    prefixes=[
        Prefix(label="major", type="major"),
        
        Prefix(label="minor", type="minor"),
        Prefix(label="feat", type="minor"),
        
        Prefix(label="patch", type="patch"),
        Prefix(label="fix", type="patch"),
    ]
)
DEFAULT_CONFIG_DICT = DEFAULT_CONFIG.model_dump()



def load_config(config_path: Path) -> None:
    if not config_path.is_file():
        return SemverConfig(**DEFAULT_CONFIG_DICT)
    with open(config_path, "r") as config_file:
        config_raw = config_file.read()
    config_dict = json.loads(config_raw)
    config_merged = {**DEFAULT_CONFIG_DICT, **config_dict}
    return SemverConfig(**config_merged)
