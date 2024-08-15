"""Module containg data types imported throughout."""

from dataclasses import dataclass
import enum
from pydantic import BaseModel, field_serializer


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


@dataclass
class Commit:
    """Represents a Git commit."""

    hash: str
    message: str


@dataclass
class Tag:
    """Represents a Semver logical tag."""

    # The formatted tag name as it appears in Git.
    name: str
    # The major part of the version.
    major: int
    # The minor part of the version.
    minor: int
    # The patch part of the version.
    patch: int
