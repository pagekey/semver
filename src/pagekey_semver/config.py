"""Module related to config files."""
import enum
from pathlib import Path
from typing import List

from pydantic import BaseModel
import yaml


class ReleaseType(enum.Enum):
    NO_RELEASE = "no release"
    PATCH = "patch"
    MINOR = "minor"
    MAJOR = "major"

class GitConfig(BaseModel):
    name: str
    email: str

class Prefix(BaseModel):
    label: str
    type: ReleaseType

class SemverConfig(BaseModel):
    git: GitConfig
    prefixes: List[Prefix]

DEFAULT_CONFIG = SemverConfig(
    git=GitConfig(
        name="PageKey Semver",
        email="semver@pagekey.io",
    ),
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
    config_dict = yaml.safe_load(config_raw)
    config_merged = {**DEFAULT_CONFIG_DICT, **config_dict}
    return SemverConfig(**config_merged)
