import abc
import enum
from typing import Literal, Union
from pydantic import BaseModel, field_serializer

from pagekey_semver.models import Tag


class ReplaceFileType(str, enum.Enum):
    """File types supported for `replace_files` in config."""

    JSON = "json"
    SED = "sed"
    TOML = "toml"
    YAML = "yaml"


class ReplaceFile(BaseModel, abc.ABC):
    """File to be replaced on new release."""

    name: str
    type: ReplaceFileType

    @field_serializer("type")
    def get_enum_value(self, v, info) -> str:
        """Turn the type field into a string when serializing."""
        return str(v.value)

    @abc.abstractmethod
    def perform_replace(self, tag: Tag) -> str:
        """Parse the `name` filepath and replace some part of it with the attributes of `tag`.
        
        Args:
            tag: The version tag to be used when replacing part of the file.
        """


class JsonReplaceFile(ReplaceFile):
    """Represents JSON file to replaced on new release."""

    type: Literal[ReplaceFileType.JSON] = ReplaceFileType.JSON
    key: str
    format: str

    def perform_replace(self, tag: Tag) -> str:
        """Replace a key in a JSON file using the provided format.
        
        Args:
            tag: Version tag to replace key with.
        """


class SedReplaceFile(ReplaceFile):
    """Represents a file to replaced using `sed` on new release."""

    type: Literal[ReplaceFileType.SED] = ReplaceFileType.SED
    script: str

    def perform_replace(self, tag: Tag) -> str:
        """Run the sed program to replace a tag in a file.
        
        Args:
            script: Sed script to run on the file.
        """


class TomlReplaceFile(ReplaceFile):
    """Represents TOML file to replaced on new release."""

    type: Literal[ReplaceFileType.TOML] = ReplaceFileType.TOML
    key: str
    format: str

    def perform_replace(self, tag: Tag) -> str:
        """Replace a key in a TOML file using the provided format.
        
        Args:
            tag: Version tag to replace key with.
        """


class YamlReplaceFile(ReplaceFile):
    """Represents YAML file to replaced on new release."""

    type: Literal[ReplaceFileType.YAML] = ReplaceFileType.YAML
    key: str
    format: str

    def perform_replace(self, tag: Tag) -> str:
        """Replace a key in a YAML file using the provided format.
        
        Args:
            tag: Version tag to replace key with.
        """


ReplaceFileUnion = Union[
    JsonReplaceFile, SedReplaceFile, TomlReplaceFile, YamlReplaceFile
]
