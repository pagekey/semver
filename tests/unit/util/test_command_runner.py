"""Test command_runner module."""

from subprocess import CompletedProcess
from unittest.mock import patch

import pytest
from pagekey_semver.util.command_runner import CommandRunnerException, SubprocessCommandRunner


MODULE_UNDER_TEST = "pagekey_semver.util.command_runner"

class TestSubprocessCommandRunner:
    
    class Test_run:

        @patch(f"{MODULE_UNDER_TEST}.subprocess")
        def test_with_successful_command_returns_command_result(self, mock_subp):
            # Arrange.
            runner = SubprocessCommandRunner()
            mock_subp.run.return_value = CompletedProcess(
                args="echo hello world",
                returncode=0,
                stdout="hello world\n",
                stderr="none\n",
            )

            # Act.
            result = runner.run("echo hello world")

            # Assert.
            mock_subp.run.assert_called()
            assert result.exit_code == 0
            assert result.stdout == "hello world\n"
            assert result.stderr == "none\n"


        @patch(f"{MODULE_UNDER_TEST}.subprocess")
        def test_with_failed_command_and_raise_flag_raises_error(self, mock_subp):
            # Arrange.
            runner = SubprocessCommandRunner()
            mock_subp.run.return_value = CompletedProcess(
                args="echo hello world",
                returncode=1,
                stdout="hello world\n",
                stderr="none\n",
            )

            # Act, Assert.
            with pytest.raises(CommandRunnerException):
                runner.run("echo hello world")


        @patch(f"{MODULE_UNDER_TEST}.subprocess")
        def test_with_failed_command_and_no_raise_flag_returns_command_result(self, mock_subp):
            # Arrange.
            runner = SubprocessCommandRunner()
            mock_subp.run.return_value = CompletedProcess(
                args="echo hello world",
                returncode=1,
                stdout="hello world\n",
                stderr="none\n",
            )

            # Act, Assert.
            result = runner.run("echo hello world", raise_on_command_fail=False)

            # Assert.
            mock_subp.run.assert_called()
            assert result.exit_code == 1
            assert result.stdout == "hello world\n"
            assert result.stderr == "none\n"
