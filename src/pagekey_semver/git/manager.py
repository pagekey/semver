"""Module for interacting with Git."""

from dataclasses import dataclass
import os
import subprocess
from typing import List, Optional
from pagekey_semver.models import SemverConfig, Commit, Tag


@dataclass
class LocalGitOptions:
    """Any Git options that will be changes by this package."""

    name: str
    email: str
    remote: str


class GitEffector:
    pass


class GitManager:
    """Class to handle all communications with Git executable."""

    def __init__(self, config: SemverConfig):
        """Initialize Git manager."""
        self._config = config

    def get_existing_git_info(self) -> LocalGitOptions:
        """Determine exisitng Git config information.

        This will allow the original configuration to be restored after run,
        which is important to avoid messing up the user's configuration when
        running locally.

        Returns:
            LocalGitOptions representing any Git options that may get changed.

        Raises:
            CalledProcessError if there is an issue calling Git to check these values.
        """
        try:
            result = subprocess.run(
                ["git", "config", "user.email"],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            email = result.stdout.strip()
        except subprocess.CalledProcessError as e:
            email = ""
        try:
            result = subprocess.run(
                ["git", "config", "user.name"],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            name = result.stdout.strip()
        except subprocess.CalledProcessError as e:
            name = ""
        try:
            result = subprocess.run(
                ["git", "config", "remote.origin.url"],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            remote = result.stdout.strip()
        except subprocess.CalledProcessError as e:
            remote = ""
        return LocalGitOptions(name=name, email=email, remote=remote)

    def get_git_tags(self) -> List[str]:
        """Get a list of all Git tags for the current repo.

        Returns:
            List of each tag name as a string.
        """
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
        """Return a  list of commit messages since a commit ref.

        Args:
            commit_hash: Reference to a commit to pull messages since, or None.

        Returns:
            Commit messages since `commit_hash` if provided.
            All commit messages if `commit_hash` is None.
        """
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
                if len(line) < 1:
                    continue
                hash = line.split()[0]
                message = line.replace(hash + " ", "")
                commits.append(Commit(hash, message))
            return commits
        except subprocess.CalledProcessError as e:
            print(f"Error getting commit messages: {e.stderr}", flush=True)
            return []

    def apply_tag(self, existing_tags: List[Tag], new_tag: Tag) -> None:
        """Commit, tag, and push.

        Changes Git username, email based on config
        and restores them to what they were previously when done.

        Args:
            existing_tags: List of pre-existing Git tags in repo.
            new_tag: Tag to be added, if it does not already exist.
        """
        if new_tag not in existing_tags:
            print(f"Tagging/pushing new tag: {new_tag}", flush=True)
            original_git_config = self.get_existing_git_info()
            self.set_git_remote()
            commands = [
                f'git config user.email "{self._config.git.email}"',
                f'git config user.name "{self._config.git.name}"',
                f"git add --all",
                f"git commit -m '{new_tag.name}'",
                f"git tag {new_tag.name}",
                f"git push origin {new_tag.name}",
                f"git push origin HEAD",
            ]
            if len(original_git_config.email) > 0:
                commands.append(f'git config user.email "{original_git_config.email}"')
            if len(original_git_config.email) > 0:
                commands.append(f'git config user.name "{original_git_config.name}"')
            if len(original_git_config.email) > 0:
                commands.append(
                    f'git config remote.origin.url "{original_git_config.remote}"'
                )
            for command in commands:
                print("Running:", command, flush=True)
                exit_code = os.system(command)
                if exit_code != 0:
                    raise ValueError(f"Command failed: {command}")
        else:
            print(f"Tag {new_tag} already exists - skipping tag/push.", flush=True)

    def set_git_remote(self):
        """."""
        pass
