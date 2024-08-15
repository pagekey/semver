"""Test Git Effector module."""

from unittest.mock import MagicMock
from pagekey_semver.git.effector import CommandGitEffector


class TestCommandGitEffector:
    class Test_set_config_item:
        def test_with_sample_key_value_calls_git(self):
            # Arrange.
            runner = MagicMock()
            querier = CommandGitEffector(runner)

            # Act.
            querier.set_config_item("user.email", "me@example.com")

            # Assert.
            runner.run.assert_called_with('git config user.email "me@example.com"')

    class Test_add_all:
        def test_with_no_args_runs_add_all(self):
            # Arrange.
            runner = MagicMock()
            querier = CommandGitEffector(runner)

            # Act.
            querier.add_all()

            # Assert.
            runner.run.assert_called_with("git add --all")

    class Test_create_commit:
        def test_with_message_adds_commit(self):
            # Arrange.
            runner = MagicMock()
            querier = CommandGitEffector(runner)

            # Act.
            querier.create_commit("my message")

            # Assert.
            runner.run.assert_called_with('git commit -m "my message"')

    class Test_create_tag:
        def test_with_tag_name_adds_tag(self):
            # Arrange.
            runner = MagicMock()
            querier = CommandGitEffector(runner)

            # Act.
            querier.create_tag("1.0.0")

            # Assert.
            runner.run.assert_called_with("git tag 1.0.0")

    class Test_push:
        def test_with_remote_and_ref_calls_git_push(self):
            # Arrange.
            runner = MagicMock()
            querier = CommandGitEffector(runner)

            # Act.
            querier.push("origin", "main")

            # Assert.
            runner.run.assert_called_with("git push origin main")
