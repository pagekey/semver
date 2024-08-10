"""Module for computing release logic. related to computing release."""

import re
from typing import List, Optional

from pagekey_semver.config import SemverConfig
from pagekey_semver.models import Commit, ReleaseType, Tag


# This variable assigns a numeric priority to each ReleaseType,
# which allows the higher numbers to take precedence over the
# lower ones.
RELEASE_TYPE_PRIORITIES = {
    ReleaseType.NO_RELEASE: 0,
    ReleaseType.PATCH: 1,
    ReleaseType.MINOR: 2,
    ReleaseType.MAJOR: 3,
}


def release_greater(a: ReleaseType, b: ReleaseType) -> bool:
    """Determine which of the two release types is greater in priority.

    Args:
        a: The first release type to compare.
        b: The second release type to compare.

    Returns:
        True if release b is greater than release a.
        False otherwise.
    """
    pri1 = RELEASE_TYPE_PRIORITIES[a]
    pri2 = RELEASE_TYPE_PRIORITIES[b]
    return pri1 < pri2


class SemverRelease:
    """Class representing a release."""

    def __init__(self, config: SemverConfig):
        """Initialize SemverRelease object.

        Args:
            config: The SemverConfig to dictate behavior.
        """
        self._config = config

    def compute_release_type(self, commits: List[Commit]) -> ReleaseType:
        """Compute release type (major/minor/patch) based on commits.

        Args:
            commits: List of commits since last tag.

        Returns:
            ReleaseType that should be generated based on these commits.
        """
        release_type = ReleaseType.NO_RELEASE
        for commit in commits:
            for prefix in self._config.prefixes:
                if commit.message.startswith(f"{prefix.label}: "):
                    # Check whether this is greater than the existing value
                    if release_greater(release_type, prefix.type):
                        release_type = prefix.type
        return release_type

    def get_matching_tags(self, tags: List[str]) -> List[Tag]:
        """Parse git tags and return Tag objects.

        Only Git tags that match the `tag_format` in the config
        will be returned.

        Args:
            tags: Full list of Git tags for current repo.

        Returns:
            List of relevant tags, parsed into Tag objects.
        """
        pattern = (
            self._config.format.replace("%M", r"(?P<major>\d+)")
            .replace("%m", r"(?P<minor>\d+)")
            .replace("%p", r"(?P<patch>\d+)")
            .replace(".", r"\.")
        )
        matches = []
        for tag in tags:
            match = re.match(pattern, tag)
            if match:
                matches.append(
                    Tag(
                        name=tag,
                        major=int(match.group("major")),
                        minor=int(match.group("minor")),
                        patch=int(match.group("patch")),
                    )
                )
        return matches

    def get_biggest_tag(self, tags: List[str]) -> Optional[Tag]:
        """Among existing tags, determine which is newest.

        Args:
            tags: Full list of Git tags.

        Returns:
            Largest tag if at least one tag was provided.
            None if the `tags` arg was an empty list.
        """
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

    def compute_next_version(self, release_type: ReleaseType, tags: List[Tag]) -> Tag:
        """Given the release type and tags, determine new tag (if any).

        Args:
            release_type: ReleaseType for next version.
            tags: List of Git tags in repo.

        Returns:
            Tag representing new version if new release needed.
            Biggest tag among existing tags if no need release needed.
        """
        if len(tags) < 1:
            name = (
                self._config.format.replace("%M", "0")
                .replace("%m", "1")
                .replace("%p", "0")
            )
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
            max_version = (
                biggest_tag.major,
                biggest_tag.minor,
                biggest_tag.patch,
            )  # NO_RELEASE

        name = (
            self._config.format.replace("%M", str(max_version[0]))
            .replace("%m", str(max_version[1]))
            .replace("%p", str(max_version[2]))
        )
        return Tag(name, max_version[0], max_version[1], max_version[2])
