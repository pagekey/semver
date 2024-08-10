"""Module to test SED file replacer."""

from unittest.mock import MagicMock

import pytest
from pagekey_semver.models import Tag
from pagekey_semver.file_replacer.sed import SedFileReplacer
from pagekey_semver.util.command_runner import CommandResult, CommandRunnerException


MODULE_UNDER_TEST = "pagekey_semver.file_replacer.sed"


class TestSedFileReplacer:
    class Test_perform_replace:
        def test_with_sed_not_installed_raises_error(self):
            # Arrange.
            tag = Tag("v2.0.0", 2, 0, 0)
            runner = MagicMock()
            runner.run.return_value = CommandResult(
                exit_code=1,
                stdout="",
                stderr="",
            )
            replacer = SedFileReplacer(
                name="file.md",
                script="s/something/other/g",
            )

            # Act, Assert.
            with pytest.raises(EnvironmentError):
                replacer.perform_replace(tag, runner)

            # Assert.
            runner.run.assert_called_with("which sed", raise_on_command_fail=False)

        @pytest.mark.parametrize(
            "input_script, tag, expected_command",
            [
                (
                    "s/something/else/g",
                    Tag("v2.0.0", 2, 0, 0),
                    "sed -i 's/something/else/g' file.md",
                ),
                (
                    's/^version=".*"/version=%M.%m.%p/g',
                    Tag("v2.0.0", 2, 0, 1),
                    "sed -i 's/^version=\".*\"/version=2.0.1/g' file.md",
                ),
                (
                    "s/^version='.*'/version=%M.%m.%p/g",
                    Tag("v2.0.0", 2, 0, 1),
                    "sed -i 's/^version=\\'.*\\'/version=2.0.1/g' file.md",
                ),
            ],
        )
        def test_with_script_calls_sed(
            self,
            input_script,
            tag,
            expected_command,
        ):
            # Arrange.
            runner = MagicMock()
            runner.run.side_effect = [
                # which shutil
                CommandResult(
                    exit_code=0,
                    stdout="",
                    stderr="",
                ),
                # running sed
                CommandResult(
                    exit_code=0,
                    stdout="",
                    stderr="",
                ),
            ]
            replacer = SedFileReplacer(
                name="file.md",
                script=input_script,
            )

            # Act.
            replacer.perform_replace(tag, runner)

            # Assert.
            runner.run.assert_called_with(expected_command)

        def test_with_failed_sed_raises_error(self):
            # Arrange.
            tag = Tag("v2.0.0", 2, 0, 0)
            replacer = SedFileReplacer(
                name="some_file.md", script="some_invalid_script"
            )

            # Act, Assert.
            with pytest.raises(CommandRunnerException):
                replacer.perform_replace(tag)
