"""Module for making changes to Git."""

import abc

from pagekey_semver.util.command_runner import CommandRunner, SubprocessCommandRunner


class GitEffector(abc.ABC):
    """Make changes to the current Git repo."""

    @abc.abstractmethod
    def set_config_item(self, key: str, value: str) -> None:
        """Set the Git config stored for the provided key.

        Args:
            key: Config key to set.
            value: Value to set.
        """

    @abc.abstractmethod
    def add_all(self) -> None:
        """Stage all current changes for commit."""

    @abc.abstractmethod
    def create_commit(self, message: str) -> None:
        """Make a new commit with the provided message.

        Args:
            message: The commit message.
        """

    @abc.abstractmethod
    def create_tag(self, name: str) -> None:
        """Create a tag with the provided name.

        Args:
            name: Name of tag to create.
        """

    @abc.abstractmethod
    def push(self, remote: str, ref: str) -> None:
        """Push a ref to a remote.

        Args:
            remote: Where to push.
            ref: Which commit, branch, or tag to push.
        """


class CommandGitEffector(GitEffector):
    """Use the Git CLI to make changes to Git."""

    def __init__(self, command_runner: CommandRunner = SubprocessCommandRunner()):
        self._runner = command_runner

    def set_config_item(self, key: str, value: str) -> None:
        self._runner.run(f'git config {key} "{value}"')

    def add_all(self) -> None:
        self._runner.run("git add --all")

    def create_commit(self, message: str) -> None:
        self._runner.run(f'git commit -m "{message}"')

    def create_tag(self, name: str) -> None:
        self._runner.run(f"git tag {name}")

    def push(self, remote: str, ref: str) -> None:
        self._runner.run(f"git push {remote} {ref}")
