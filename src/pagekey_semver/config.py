"""Module related to config files."""
import enum
import json
import os
from pathlib import Path
from typing import Dict, List, Literal, Union

from pydantic import BaseModel, Field, field_serializer
import yaml

from pagekey_semver.util.variable_parser import VariableParser


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

    @field_serializer('type')
    def serialize_type(self, type: ReleaseType, _info):
        return type.value


class ReplaceFileType(str, enum.Enum):
    JSON = "json"
    SED = "sed"
    TOML = "toml"
    YAML = "yaml"

class ReplaceFile(BaseModel):
    name: str
    type: ReplaceFileType

    @field_serializer('type')
    def get_eunm_value(self, v, info) -> str:
        return str(v.value)

class JsonReplaceFile(ReplaceFile):
    type: Literal[ReplaceFileType.JSON] = ReplaceFileType.JSON
    key: str

class SedReplaceFile(ReplaceFile):
    type: Literal[ReplaceFileType.SED] = ReplaceFileType.SED
    script: str

class TomlReplaceFile(ReplaceFile):
    type: Literal[ReplaceFileType.TOML] = ReplaceFileType.TOML
    key: str

class YamlReplaceFile(ReplaceFile):
    type: Literal[ReplaceFileType.YAML] = ReplaceFileType.YAML
    key: str

ReplaceFileUnion = Union[JsonReplaceFile, SedReplaceFile, TomlReplaceFile, YamlReplaceFile]


class SemverConfig(BaseModel):
    changelog_path: str
    changelog_writer: str
    format: str
    git: GitConfig
    prefixes: List[Prefix]
    replace_files: List[ReplaceFileUnion] = Field(discriminator="type")


DEFAULT_CONFIG = SemverConfig(
    changelog_path="CHANGELOG.md",
    changelog_writer="pagekey_semver.changelog:DefaultChangelogWriter",
    format="v%M.%m.%p",
    git=GitConfig(
        name="PageKey Semver",
        email="semver@pagekey.io",
    ),
    prefixes=[
        Prefix(label="major", type="major"),
        
        Prefix(label="minor", type="minor"),
        Prefix(label="feat", type="minor"),
        Prefix(label="fix", type="patch"),
    ],
    replace_files=[],
)
DEFAULT_CONFIG_DICT = DEFAULT_CONFIG.model_dump()


def load_config(config_path: Path) -> SemverConfig:
    # Get the file config.
    if config_path.is_file():
        with open(config_path, "r") as file_handle:
            custom_config = yaml.safe_load(file_handle.read())
        config_without_env = {**DEFAULT_CONFIG_DICT, **custom_config}
    else:
        config_without_env = DEFAULT_CONFIG_DICT
    
    # Get the config defined by environment variables.
    variable_parser = VariableParser(os.environ)
    env_config = variable_parser.get_config()
    
    # Merge the file config and the environment config.
    # Environment takes precedence.
    final_config = {**config_without_env, **env_config}
    return SemverConfig(**final_config)
