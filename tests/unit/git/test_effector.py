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
