"""Module for interacting with Git."""

import os
import subprocess
from typing import List, Optional
from pagekey_semver.models import SemverConfig
from pagekey_semver.release import Commit, Tag


class GitManager:
    """."""

    def __init__(self, config: SemverConfig):
        """."""
        self._config = config

    def get_git_tags(self) -> List[str]:
        """."""
        try:
            result = subprocess.run(
                ["git", "tag"],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            # Split the output into lines (each tag is on a new line)
            tags = result.stdout.strip().split("\n")
            return tags
        except subprocess.CalledProcessError as e:
            print(f"Error getting git tags: {e.stderr}", flush=True)
            return []

    def get_commit_messages_since(self, commit_hash: Optional[str]) -> List[Commit]:
        """."""
        try:
            if commit_hash is None:
                args = ["git", "log", "--pretty=format:%H %s"]
            else:
                args = ["git", "log", f"{commit_hash}..HEAD", "--pretty=format:%H %s"]
            result = subprocess.run(
                args,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            # Split the output into lines (each line is a commit message)
            commit_lines = result.stdout.strip().split("\n")
            commits = []
            for line in commit_lines:
                hash = line.split()[0]
                message = line.replace(hash + " ", "")
                commits.append(Commit(hash, message))
            return commits
        except subprocess.CalledProcessError as e:
            print(f"Error getting commit messages: {e.stderr}", flush=True)
            return []

    def apply_tag(self, existing_tags: List[Tag], new_tag: Tag):
        """."""
        if new_tag not in existing_tags:
            print(f"Tagging/pushing new tag: {new_tag}", flush=True)
            commands = [
                f"git config user.email {self._config.git.email}",
                f'git config user.name "{self._config.git.name}"',
                f"git add --all",
                f"git commit -m '{new_tag.name}'",
                f"git tag {new_tag.name}",
                f"git push origin {new_tag.name}",
                f"git push origin HEAD",
            ]
            for command in commands:
                print("Running:", command, flush=True)
                exit_code = os.system(command)
                if exit_code != 0:
                    raise ValueError(f"Command failed: {command}")
        else:
            print(f"Tag {new_tag} already exists - skipping tag/push.", flush=True)
