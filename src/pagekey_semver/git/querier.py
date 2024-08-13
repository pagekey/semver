"""Module for querying Git."""

import abc
from typing import List, Optional

from pagekey_semver.models import Commit
from pagekey_semver.util.command_runner import (
    CommandRunner,
    CommandRunnerException,
    SubprocessCommandRunner,
)


class GitQuerier(abc.ABC):
    """Query the current Git repo for data."""

    @abc.abstractmethod
    def get_config_item(self, key: str) -> str:
        """Get the Git config stored for the provided key.

        Args:
            key: Config key to retrieve.

        Returns:
            The value of the config key.
        """

    @abc.abstractmethod
    def get_tag_names(self) -> List[str]:
        """Get a list of all Git tag names for the current repo.

        Returns:
            List of each tag name as a string.
        """

    @abc.abstractmethod
    def get_commits(self, since_ref: Optional[str] = None) -> List[str]:
        """Return commits in this repo since provided ref, or all commits.

        Args:
            since_ref: Reference to a commit to pull messages since, or None.

        Returns:
            Commits since `commit_hash` if provided.
            All commits if `commit_hash` is None.
        """


class CommandGitQuerier(GitQuerier):
    """Use the Git CLI to query Git."""

    def __init__(self, command_runner: CommandRunner = SubprocessCommandRunner()):
        self._runner = command_runner

    def get_config_item(self, key: str):
        try:
            result = self._runner.run(f"git config {key}")
            return result.stdout.strip()
        except CommandRunnerException:
            print(f"Failed to retrieve git config key {key}")
            return ""

    def get_tag_names(self) -> List[str]:
        result = self._runner.run("git tag")
        # Filter out empty strings and return.
        return [tag for tag in result.stdout.split() if len(tag) > 0]

    def get_commits(self, since_ref: Optional[str] = None) -> List[str]:
        # Create command.
        command = 'git log --pretty="format:%H %s"'
        if since_ref is not None and len(since_ref) > 0:
            command += f" {since_ref}..HEAD"
        # Run the command.
        command_result = self._runner.run(command)
        # Parse the commit messages.
        commits = []
        for commit_log in command_result.stdout.split("\n"):
            # Ignore blank lines.
            if len(commit_log) == 0:
                continue
            # Separate the hash from the commit message.
            fields = commit_log.split()
            commits.append(
                Commit(
                    hash=fields[0],
                    message=" ".join(fields[1:]),
                )
            )
        return commits
