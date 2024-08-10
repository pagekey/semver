from typing import Literal

from pagekey_semver.models import Tag
from pagekey_semver.file_replacer.base import FileReplacer, FileReplacerType
from pagekey_semver.util.command_runner import CommandRunner, SubprocessCommandRunner


class SedFileReplacer(FileReplacer):
    """Represents a file to replaced using `sed` on new release."""

    type: Literal[FileReplacerType.SED] = FileReplacerType.SED
    script: str

    def perform_replace(
        self, tag: Tag, runner: CommandRunner = SubprocessCommandRunner()
    ) -> str:
        """Run the sed program to replace a tag in a file.

        Replaces %M/%m/%p with tag's major/minor/patch,
        then calls sed with the provided `script`.

        Args:
            script: Sed script to run on the file.
        """
        # Check if the sed executable is available.
        result = runner.run("which sed", raise_on_command_fail=False)
        if result.exit_code != 0:
            raise EnvironmentError(
                "Sed executable not found on system - have you installed sed?"
            )
        # Replace placeholders in script using tag's major/minor/patch.
        script_escaped = self.script.replace("'", "\\'")
        script_replaced = (
            script_escaped.replace("%M", str(tag.major))
            .replace("%m", str(tag.minor))
            .replace("%p", str(tag.patch))
        )
        # Run sed.
        runner.run(f"sed -i '{script_replaced}' {self.name}")
