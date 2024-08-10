import abc
import enum
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