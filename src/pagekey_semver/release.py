"""Module for computing release logic. related to computing release."""


from dataclasses import dataclass
import re
from typing import List, Optional

from pagekey_semver.config import ReleaseType, SemverConfig


@dataclass
class Commit:
    hash: str
    message: str

@dataclass
class Tag:
    name: str
    major: int
    minor: int
    patch: int

RELEASE_TYPE_PRIORITIES = {
    ReleaseType.NO_RELEASE: 0,
    ReleaseType.PATCH: 1,
    ReleaseType.MINOR: 2,
    ReleaseType.MAJOR: 3,
}


PREFIXES = {
    "fix": ReleaseType.PATCH,
    "feat": ReleaseType.MINOR,
    "major": ReleaseType.MAJOR,
}


def release_greater(a: ReleaseType, b: ReleaseType) -> bool:
    pri1 = RELEASE_TYPE_PRIORITIES[a]
    pri2 = RELEASE_TYPE_PRIORITIES[b]
    return pri1 < pri2


class SemverRelease:

    def __init__(self, config: SemverConfig):
        self._config = config

    def compute_release_type(self, commits: List[Commit]) -> ReleaseType:
        """."""
        release_type = ReleaseType.NO_RELEASE
        for commit in commits:
            for prefix in self._config.prefixes:
                if commit.message.startswith(f"{prefix.label}: "):
                    # Check whether this is greater than the existing value
                    if release_greater(release_type, prefix.type):
                        release_type = prefix.type
        return release_type


    def get_matching_tags(self, tags: List[str]) -> List[Tag]:
        pattern = self._config.format \
            .replace("%M", r"(?P<major>\d+)") \
            .replace("%m", r"(?P<minor>\d+)") \
            .replace("%p", r"(?P<patch>\d+)") \
            .replace(".",  r"\.")
        matches = []
        for tag in tags:
            match = re.match(pattern, tag)
            if match:
                matches.append(Tag(
                    name=tag, 
                    major=int(match.group('major')), 
                    minor=int(match.group('minor')), 
                    patch=int(match.group('patch')),
                ))
        return matches


    def get_biggest_tag(self, tags: List[str]) -> Optional[Tag]:
        tags = self.get_matching_tags(tags)
        max_tag = None
        for tag in tags:
                if (
                    max_tag is None
                    or tag.major > max_tag.major
                    or (tag.major == max_tag.major and tag.minor > max_tag.minor)
                    or (
                        tag.major == max_tag.major
                        and tag.minor == max_tag.minor
                        and tag.patch > max_tag.patch
                    )
                ):
                    max_tag = tag
        return max_tag


    def compute_next_version(self, release_type: ReleaseType, tags: List[Tag]) -> Optional[Tag]:
        """."""
        if len(tags) < 1:
            name = self._config.format \
                .replace("%M", "0") \
                .replace("%m", "1") \
                .replace("%p", "0")
            return Tag(name, 0, 1, 0)
        biggest_tag = self.get_biggest_tag(tags)
        if biggest_tag is None:
            max_version = (0, 1, 0)
        elif release_type == ReleaseType.MAJOR:
            max_version = (biggest_tag.major + 1, 0, 0)
        elif release_type == ReleaseType.MINOR:
            max_version = (biggest_tag.major, biggest_tag.minor + 1, 0)
        elif release_type == ReleaseType.PATCH:
            max_version = (biggest_tag.major, biggest_tag.minor, biggest_tag.patch + 1)
        else:
            max_version = (biggest_tag.major, biggest_tag.minor, biggest_tag.patch)  # NO_RELEASE

        name = self._config.format \
            .replace("%M", str(max_version[0])) \
            .replace("%m", str(max_version[1])) \
            .replace("%p", str(max_version[2]))
        return Tag(name, max_version[0], max_version[1], max_version[2])
