import abc
from typing import List

from pagekey_semver.config import SemverConfig
from pagekey_semver.release import Commit, Tag


class ChangelogWriter(abc.ABC):

    @abc.abstractmethod
    def __init__(self, config: SemverConfig):
        """Initialize the writer."""
    
    @abc.abstractmethod
    def update_changelog(self, version: Tag, commits: List[Commit]) -> None:
        """Update the changelog file.
        
        Args:
            version: The new version being added.
            commits: The commits associated with the new version.
        """


class DefaultChangelogWriter(ChangelogWriter):

    def __init__(self, config: SemverConfig) -> None:
        self._config = config

    def update_changelog(self, version: Tag, commits: List[Commit]) -> None:
        with open("CHANGELOG.md", "a") as changelog_file:
            changelog_file.write(f"## {version.name}\n\n")
            for commit in commits:
                for prefix in self._config.prefixes:
                    if commit.message.startswith(f"{prefix.label}: "):
                        changelog_file.write(f"- {commit.message} ({commit.hash})\n")
            changelog_file.write("\n")
