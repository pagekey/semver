"""Module for writing changelogs."""

from __future__ import annotations
import abc
import os
import tempfile
from typing import List, TextIO

from pagekey_semver.util.dynamic_import import dynamic_import
from pagekey_semver.config import SemverConfig
from pagekey_semver.models import Commit, Tag


class ChangelogWriter(abc.ABC):
    """Base class for all ChangelogWriters."""

    @staticmethod
    def from_config(config: SemverConfig) -> ChangelogWriter:
        """Create a ChangelogWriter from a config file.

        Uses the `changelog_writer` string to dynamically import a Changelog class for use.

        Args:
            Config that defines where the ChangelogWriter class is.

        Returns:
            ChangelogWriter instance with imported class, initialized with config.

        Raises:
            ImportError, AttributeError if the import string is not valid.
        """
        changelog_writer_cls = dynamic_import(config.changelog_writer)
        return changelog_writer_cls(config)

    def __init__(self, config: SemverConfig):
        """Initialize the writer.

        Args:
            config: Semver application config.
        """
        self._config = config

    def update_changelog(self, version: Tag, commits: List[Commit]) -> None:
        """Update changelog.

        This is the method called by the CLI to perform the update.

        It contains a few additional methods to simplify the implementation
        of write_changelog, which can be overridden by the user.

        Args:
            version: The new version being added.
            commits: Full list of commits since last release.
        """
        self._create_dirs()
        filtered_commits = self._filter_commits(commits)
        # Write new version info to temp file.
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp_file:
            self.write_changelog(temp_file, version, filtered_commits)
            # Write existing changelog to temp file.
            if os.path.exists(self._config.changelog_path):
                with open(self._config.changelog_path, "r") as changelog_file:
                    temp_file.write(changelog_file.read())
            temp_file_name = temp_file.name
        with open(temp_file_name, "r") as temp_file:
            # Copy temp file to changelog, effectively prepending.
            with open(self._config.changelog_path, "w") as changelog_file:
                changelog_file.write(temp_file.read())
        # Delete temp_file
        os.unlink(temp_file_name)

    def _filter_commits(self, commits: List[Commit]) -> List[Commit]:
        """Filter out any commits that do not start with a valid prefix.

        Args:
            commits: Full list of commits since last release.

        Returns:
            List of commits that start with a prefix defined in config.
        """
        result = []
        for commit in commits:
            for prefix in self._config.prefixes:
                if commit.message.startswith(f"{prefix.label}: "):
                    result.append(commit)
        return result

    def _create_dirs(self) -> None:
        """Make directories for Changelog."""
        dirs = os.path.dirname(self._config.changelog_path)
        if len(dirs) > 0:
            os.makedirs(dirs, exist_ok=True)

    @abc.abstractmethod
    def write_changelog(
        self, changelog_file: TextIO, version: Tag, commits: List[Commit]
    ) -> None:
        """Update the changelog file.

        Args:
            version: The new version being added.
            commits: The commits associated with the new version.
        """


class DefaultChangelogWriter(ChangelogWriter):
    """Default concrete implementation of ChangelogWriter.

    Writes a simple CHANGELOG file with a level-2 header for each release
    and a bullet containing message and commit hash for each commit in the release.
    """

    def write_changelog(
        self, changelog_file: TextIO, version: Tag, commits: List[Commit]
    ) -> None:
        """Update the changelog file.

        Args:
            version: The new version being added.
            commits: The commits associated with the new version.
        """
        # Write changelog.
        changelog_file.write(f"## {version.name}\n\n")
        for commit in commits:
            changelog_file.write(f"- {commit.message} ({commit.hash[0:8]})\n")
        changelog_file.write("\n")
