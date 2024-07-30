from typing import List

from pagekey_semver.config import SemverConfig
from pagekey_semver.release import Commit


class ChangelogWriter:

    def __init__(self, config: SemverConfig):
        self._config = config

    def update_changelog(self, version: str, commits: List[Commit]):
        with open("CHANGELOG.md", "a") as changelog_file:
            changelog_file.write(f"## {version}\n\n")
            for commit in commits:
                if commit.message.startswith("fix: ") or commit.message.startswith("feat: ") or commit.message.startswith("major: "):
                    changelog_file.write(f"- {commit.message} ({commit.hash})\n")
            changelog_file.write("\n")
