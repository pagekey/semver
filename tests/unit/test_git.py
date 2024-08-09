"""Test Git module."""

from unittest.mock import MagicMock, call, patch

from pagekey_semver.config import DEFAULT_CONFIG
from pagekey_semver.models import GitConfig, SemverConfig
from pagekey_semver.git import GitManager
from pagekey_semver.release import Tag


MODULE_UNDER_TEST = "pagekey_semver.git"


class TestGitManager:
    class Test_get_git_tags:
        @patch("subprocess.run")
        def test_with_no_fail_returns_list_of_tags(self, mock_run):
            # Arrange.
            mock_result = MagicMock()
            mock_result.stdout = "tag1\ntag2"
            mock_run.return_value = mock_result
            manager = GitManager(DEFAULT_CONFIG)

            # Act.
            result = manager.get_git_tags()

            # Assert.
            mock_run.assert_called_with(
                "git tag".split(),
                check=True,
                stdout=-1,
                stderr=-1,
                text=True,
            )
            assert result[0] == "tag1"
            assert result[1] == "tag2"

    class Test_get_commit_messages:
        @patch("subprocess.run")
        def test_with_valid_hash_returns_list_of_messages(self, mock_run):
            # Arrange.
            mock_result = MagicMock()
            mock_result.stdout = "aaaaa1 Do something\naaaaa2 Do something else"
            mock_run.return_value = mock_result
            manager = GitManager(DEFAULT_CONFIG)

            # Act.
            result = manager.get_commit_messages_since("HEAD~2")

            # Assert.
            mock_run.assert_called_with(
                [
                    "git",
                    "log",
                    "HEAD~2..HEAD",
                    "--pretty=format:%H %s",
                ],
                check=True,
                stdout=-1,
                stderr=-1,
                text=True,
            )
            assert result[0].hash == "aaaaa1"
            assert result[0].message == "Do something"
            assert result[1].hash == "aaaaa2"
            assert result[1].message == "Do something else"

    class Test_apply_tag:
        @patch("subprocess.run")
        def test_with_existing_tag_does_nothing(self, mock_run):
            # Arrange.
            existing_tags = ["v0.1.0", "v3.0.0", "v2.0.0"]
            new_tag = "v3.0.0"
            manager = GitManager(DEFAULT_CONFIG)

            # Act.
            result = manager.apply_tag(existing_tags, new_tag)

            # Assert.
            mock_run.assert_not_called()

        @patch("os.system")
        def test_with_new_tag_tags_and_pushes(self, mock_system):
            # Arrange.
            existing_tags = ["v0.1.0", "v3.0.0", "v2.0.0"]
            new_tag = Tag("v4.0.0", 4, 0, 0)
            new_tag_stripped = "4.0.0"
            mock_system.return_value = 0  # exit code
            manager = GitManager(DEFAULT_CONFIG)

            # Act.
            manager.apply_tag(existing_tags, new_tag)

            # Assert.
            commands = [
                f"git config user.email semver@pagekey.io",
                f'git config user.name "PageKey Semver"',
                f"git add --all",
                f"git commit -m '{new_tag.name}'",
                f"git tag {new_tag.name}",
                f"git push origin {new_tag.name}",
            ]
            mock_system.assert_has_calls([call(command) for command in commands])

        @patch("os.system")
        def test_with_config_applies_config_name_email(self, mock_system):
            existing_tags = ["v0.1.0", "v3.0.0", "v2.0.0"]
            new_tag = Tag("v4.0.0", 4, 0, 0)
            mock_system.return_value = 0  # exit code
            config = SemverConfig(
                changelog_path="CHANGELOG.md",
                changelog_writer="pagekey_semver.changelog:ChangelogWriter",
                format="v%M.%m.%p",
                git=GitConfig(
                    name="some name",
                    email="some@email.com",
                ),
                prefixes=[],
                replace_files=[],
            )
            manager = GitManager(config)

            # Act.
            manager.apply_tag(existing_tags, new_tag)

            # Assert.
            mock_system.assert_has_calls(
                [
                    call("git config user.email some@email.com"),
                    call('git config user.name "some name"'),
                ]
            )
