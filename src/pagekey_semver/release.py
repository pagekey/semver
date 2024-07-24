"""Module for computing release logic. related to computing release."""


from dataclasses import dataclass
import enum
import re
from typing import List


@dataclass
class Commit:
    hash: str
    message: str


class ReleaseType(enum.Enum):
    NO_RELEASE = 0
    PATCH = 1
    MINOR = 2
    MAJOR = 3


PREFIXES = {
    "fix": ReleaseType.PATCH,
    "feat": ReleaseType.MINOR,
    "major": ReleaseType.MAJOR,
}


def compute_release_type(commits: List[Commit]) -> ReleaseType:
    """."""
    release_type = ReleaseType.NO_RELEASE
    for commit in commits:
        for prefix, prefix_release_type in PREFIXES.items():
            if commit.message.startswith(f"{prefix}: "):
                # Check whether this is greater than the existing value
                if release_type.value < prefix_release_type.value:
                    release_type = prefix_release_type
    return release_type


def get_biggest_tag(tags: List[str]):
    pattern = r"^v\d+\.\d+\.\d+$"
    max_version = (0, 1, 0)
    for tag in tags:
        if re.match(pattern, tag):
            # This tag has valid format (vX.Y.Z)
            major, minor, patch = tag.replace("v", "").split(".")
            major = int(major)
            minor = int(minor)
            patch = int(patch)
            if (
                major > max_version[0]
                or (major == max_version[0] and minor > max_version[1])
                or (
                    major == max_version[0]
                    and minor == max_version[1]
                    and patch > max_version[2]
                )
            ):
                max_version = (major, minor, patch)
    return f"v{max_version[0]}.{max_version[1]}.{max_version[2]}"


def compute_next_version(release_type: ReleaseType, tags: List[str]) -> str:
    """."""
    if len(tags) < 1:
        return "v0.1.0"
    major, minor, patch = get_biggest_tag(tags).replace("v", "").split(".")
    max_version = (int(major), int(minor), int(patch))
    if release_type == ReleaseType.MAJOR:
        max_version = (max_version[0] + 1, 0, 0)
    elif release_type == ReleaseType.MINOR:
        max_version = (max_version[0], max_version[1] + 1, 0)
    elif release_type == ReleaseType.PATCH:
        max_version = (max_version[0], max_version[1], max_version[2] + 1)
    else:
        pass  # NO_RELEASE

    return f"v{max_version[0]}.{max_version[1]}.{max_version[2]}"
