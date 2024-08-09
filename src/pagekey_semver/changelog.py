"""."""

import abc
import os
from typing import List, TextIO

from pagekey_semver.util.dynamic_import import dynamic_import
from pagekey_semver.models import SemverConfig
from pagekey_semver.release import Commit, Tag


class ChangelogWriter(abc.ABC):
    @staticmethod
    def from_config(config: SemverConfig):
        changelog_writer_cls = dynamic_import(config.changelog_writer)
        return changelog_writer_cls(config)

    def __init__(self, config: SemverConfig):
        """Initialize the writer."""
        self._config = config

    def update_changelog(self, version, commits):
        self._create_dirs()
        filtered_commits = self._filter_commits(commits)
        with open(self._config.changelog_path, "a") as changelog_file:
            self.write_changelog(changelog_file, version, filtered_commits)

    def _filter_commits(self, commits: List[Commit]):
        result = []
        for commit in commits:
            for prefix in self._config.prefixes:
                if commit.message.startswith(f"{prefix.label}: "):
                    result.append(commit)
        return result

    def _create_dirs(self):
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
    def write_changelog(
        self, changelog_file: TextIO, version: Tag, commits: List[Commit]
    ) -> None:
        # Write changelog
        changelog_file.write(f"## {version.name}\n\n")
        for commit in commits:
            changelog_file.write(f"- {commit.message} ({commit.hash})\n")
        changelog_file.write("\n")
