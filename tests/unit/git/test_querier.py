from unittest.mock import MagicMock
from pagekey_semver.git.querier import CommandGitQuerier
from pagekey_semver.models import Commit
from pagekey_semver.util.command_runner import CommandResult


class TestCommandGitQuerier:
    class Test_get_config_item:
        def test_with_sample_key_calls_git(self):
            # Arrange.
            runner = MagicMock()
            querier = CommandGitQuerier(runner)
            runner.run.return_value = ""
            runner.run.return_value = CommandResult(
                exit_code=0,
                stdout="me@example.com\n",
                stderr="",
            )

            # Act.
            result = querier.get_config_item("user.email")

            # Assert.
            runner.run.assert_called_with("git config user.email")
            assert result == "me@example.com"

    class Test_get_tag_names:
        def test_with_no_args_gets_all_tags(self):
            # Arrange.
            runner = MagicMock()
            querier = CommandGitQuerier(runner)
            runner.run.return_value = CommandResult(
                exit_code=0,
                stdout="tag1\ntag2\ntag3\n",
                stderr="",
            )

            # Act.
            result = querier.get_tag_names()

            # Assert.
            runner.run.assert_called_with("git tag")
            assert result == ["tag1", "tag2", "tag3"]

    class Test_get_commits:
        def test_with_no_args_returns_all_commits(self):
            # Arrange.
            runner = MagicMock()
            querier = CommandGitQuerier(runner)
            runner.run.return_value = CommandResult(
                exit_code=0,
                stdout="abcdef fix: Some commit\n123456 Initial commit\n",
                stderr="",
            )

            # Act.
            result = querier.get_commits()

            # Assert.
            runner.run.assert_called_with('git log --pretty="format:%H %s"')
            assert result == [
                Commit(hash="abcdef", message="fix: Some commit"),
                Commit(hash="123456", message="Initial commit"),
            ]


        def test_with_ref_returns_since_ref(self):
            # Arrange.
            runner = MagicMock()
            querier = CommandGitQuerier(runner)
            runner.run.return_value = CommandResult(
                exit_code=0,
                stdout="abcdef fix: Some commit\n123456 Initial commit\n",
                stderr="",
            )

            # Act.
            result = querier.get_commits("v1.0.0")

            # Assert.
            runner.run.assert_called_with('git log --pretty="format:%H %s" v1.0.0..HEAD')
            assert result == [
                Commit(hash="abcdef", message="fix: Some commit"),
                Commit(hash="123456", message="Initial commit"),
            ]
