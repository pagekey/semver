from typing import List

from pagekey_semver.release import Commit


def update_changelog(version: str, commits: List[Commit]):
    with open("CHANGELOG.md", "a") as changelog_file:
        changelog_file.write(f"## {version}\n\n")
        for commit in commits:
            if commit.message.startswith("fix: ") or commit.message.startswith("feat: ") or commit.message.startswith("major: "):
                changelog_file.write(f"- {commit.message} ({commit.hash})\n")
        changelog_file.write("\n")
