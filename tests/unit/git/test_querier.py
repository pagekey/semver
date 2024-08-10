from unittest.mock import MagicMock
from pagekey_semver.git.querier import CommandGitQuerier
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
            assert result == "me@example.com"
            runner.run.assert_called_with("git config user.email")

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
            assert result == ["tag1", "tag2", "tag3"]
            runner.run.assert_called_with("git tag")

    class Test_get_commits:
        def test_with_no_args_returns_all_commits(self):
            pass

        def test_with_ref_returns_since_ref(self):
            pass
