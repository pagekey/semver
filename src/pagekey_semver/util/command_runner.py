"""Module for running commands on the system."""

import abc
import subprocess
from dataclasses import dataclass


@dataclass
class CommandResult:
    """Information returned when executing a command."""

    exit_code: int
    stdout: str
    stderr: str


class CommandRunnerException(Exception):
    """Raised when a command does not complete successfully."""

    def __init__(self, command_result: CommandResult):
        self.command_result = command_result
        super().__init__(
            "Failed to run command: "
            f"returned code {self.command_result.exit_code}\n"
            f"{self.command_result.stdout}\n"
            f"{self.command_result.stderr}"
        )


class CommandRunner(abc.ABC):
    """Run commands on the system and return relevant info."""

    @abc.abstractmethod
    def run(self, command: str, raise_on_command_fail: bool = True) -> CommandResult:
        """Run the command on the system.

        Args:
            command: The command to run.
            raise_on_command_fail: Whether to raise an error if the command is not successful.

        Raises:
            CommandFailedException when the command returns a nonzero exit code and raise_on_command_fail is True.
        """


class SubprocessCommandRunner(CommandRunner):
    """Use the subprocess module to run commands."""

    def run(self, command: str, raise_on_command_fail: bool = True) -> CommandResult:
        # Invoke the command on the system.
        subprocess_result = subprocess.run(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        # Create the result object.
        command_result = CommandResult(
            exit_code=subprocess_result.returncode,
            stdout=subprocess_result.stdout.decode(),
            stderr=subprocess_result.stderr.decode(),
        )
        # Check exit code and fail if appropriate.
        if subprocess_result.returncode != 0 and raise_on_command_fail:
            raise CommandRunnerException(command_result)
        # Return result.
        return command_result
