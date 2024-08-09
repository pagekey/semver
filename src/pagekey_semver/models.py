"""Module containg data types imported throughout."""

import enum
from typing import List, Literal, Union
from pydantic import BaseModel, Field, field_serializer


class ReleaseType(enum.Enum):
    """."""

    NO_RELEASE = "no release"
    PATCH = "patch"
    MINOR = "minor"
    MAJOR = "major"


class GitConfig(BaseModel):
    """."""

    name: str
    email: str


class Prefix(BaseModel):
    """."""

    label: str
    type: ReleaseType

    @field_serializer("type")
    def serialize_type(self, type: ReleaseType, _info):
        return type.value


class ReplaceFileType(str, enum.Enum):
    """."""

    JSON = "json"
    SED = "sed"
    TOML = "toml"
    YAML = "yaml"


class ReplaceFile(BaseModel):
    """."""

    name: str
    type: ReplaceFileType

    @field_serializer("type")
    def get_enum_value(self, v, info) -> str:
        """."""
        return str(v.value)


class JsonReplaceFile(ReplaceFile):
    """."""

    type: Literal[ReplaceFileType.JSON] = ReplaceFileType.JSON
    key: str


class SedReplaceFile(ReplaceFile):
    """."""

    type: Literal[ReplaceFileType.SED] = ReplaceFileType.SED
    script: str


class TomlReplaceFile(ReplaceFile):
    """."""

    type: Literal[ReplaceFileType.TOML] = ReplaceFileType.TOML
    key: str


class YamlReplaceFile(ReplaceFile):
    """."""

    type: Literal[ReplaceFileType.YAML] = ReplaceFileType.YAML
    key: str


ReplaceFileUnion = Union[
    JsonReplaceFile, SedReplaceFile, TomlReplaceFile, YamlReplaceFile
]


class SemverConfig(BaseModel):
    """."""

    changelog_path: str
    changelog_writer: str
    format: str
    git: GitConfig
    prefixes: List[Prefix]
    replace_files: List[ReplaceFileUnion] = Field(discriminator="type")
