"""Module related to config files."""
import enum
import json
from pathlib import Path
from typing import List, Literal, Union

from pydantic import BaseModel, Field, field_serializer
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
        
        Prefix(label="patch", type="patch"),
        Prefix(label="fix", type="patch"),
    ],
    replace_files=[],
)
DEFAULT_CONFIG_DICT = DEFAULT_CONFIG.model_dump()


def load_config(config_path: Path) -> SemverConfig:
    if not config_path.is_file():
        return apply_env_to_config_dict(DEFAULT_CONFIG_DICT)
    with open(config_path, "r") as config_file:
        config_raw = config_file.read()
    config_dict = yaml.safe_load(config_raw)
    config_merged = {**DEFAULT_CONFIG_DICT, **config_dict}
    print(f"Loaded config:", json.dumps(config_merged))
    return apply_env_to_config_dict(config_merged)


def apply_env_to_config_dict(config_dict: dict) -> SemverConfig:
    return SemverConfig(**config_dict)
