"""Module containg data types imported throughout."""

import enum
from typing import List, Literal, Union
from pydantic import BaseModel, Field, field_serializer


class ReleaseType(enum.Enum):
    """Logical type of semantic versioning release."""

    NO_RELEASE = "no release"
    PATCH = "patch"
    MINOR = "minor"
    MAJOR = "major"


class GitConfig(BaseModel):
    """Git configuration options to set before committing."""

    name: str
    email: str


class Prefix(BaseModel):
    """Commit prefix that can trigger releases."""

    label: str
    type: ReleaseType

    @field_serializer("type")
    def serialize_type(self, type: ReleaseType, _info):
        """Convert ReleaseType to a string when serializing."""
        return type.value


class ReplaceFileType(str, enum.Enum):
    """File types supported for `replace_files` in config."""

    JSON = "json"
    SED = "sed"
    TOML = "toml"
    YAML = "yaml"


class ReplaceFile(BaseModel):
    """File to be replaced on new release."""

    name: str
    type: ReplaceFileType

    @field_serializer("type")
    def get_enum_value(self, v, info) -> str:
        """Turn the type field into a string when serializing."""
        return str(v.value)


class JsonReplaceFile(ReplaceFile):
    """Represents JSON file to replaced on new release."""

    type: Literal[ReplaceFileType.JSON] = ReplaceFileType.JSON
    key: str
    format: str


class SedReplaceFile(ReplaceFile):
    """Represents a file to replaced using `sed` on new release."""

    type: Literal[ReplaceFileType.SED] = ReplaceFileType.SED
    script: str


class TomlReplaceFile(ReplaceFile):
    """Represents TOML file to replaced on new release."""

    type: Literal[ReplaceFileType.TOML] = ReplaceFileType.TOML
    key: str
    format: str


class YamlReplaceFile(ReplaceFile):
    """Represents YAML file to replaced on new release."""

    type: Literal[ReplaceFileType.YAML] = ReplaceFileType.YAML
    key: str
    format: str


ReplaceFileUnion = Union[
    JsonReplaceFile, SedReplaceFile, TomlReplaceFile, YamlReplaceFile
]


class SemverConfig(BaseModel):
    """Represents config options for entire application."""

    changelog_path: str
    changelog_writer: str
    format: str
    git: GitConfig
    prefixes: List[Prefix]
    replace_files: List[ReplaceFileUnion] = Field(discriminator="type")
