"""Test Git module."""

from unittest.mock import MagicMock, call, patch

from pagekey_semver.config import DEFAULT_CONFIG
from pagekey_semver.models import GitConfig, SemverConfig
from pagekey_semver.git.manager import GitManager, LocalGitOptions
from pagekey_semver.models import Tag


MODULE_UNDER_TEST = "pagekey_semver.git.manager"


class TestGitManager:
    class Test_get_existing_git_info:
        @patch("subprocess.run")
        def test_with_successful_call_returns_gitconfig(self, mock_run):
            # Arrange.
            mock_git_querier = MagicMock()
            mock_git_querier.get_config_item.side_effect = [
                "me",
                "email@email.com",
                "some_remote",
            ]
            mock_git_effector = MagicMock()
            manager = GitManager(DEFAULT_CONFIG, mock_git_querier, mock_git_effector)

            # Act.
            result = manager.get_existing_git_info()

            # Assert.
            mock_git_querier.get_config_item.assert_has_calls([
                call("user.name"),
                call("user.email"),
                call("remote.origin.url"),
            ])
            assert result.email == "email@email.com"
            assert result.name == "me"
            assert result.remote == "some_remote"

    class Test_get_git_tags:
        @patch("subprocess.run")
        def test_with_no_fail_returns_list_of_tags(self, mock_run):
            # Arrange.
            mock_git_querier = MagicMock()
            mock_git_querier.get_tag_names.return_value = ["tag1", "tag2"]
            mock_git_effector = MagicMock()
            manager = GitManager(DEFAULT_CONFIG, mock_git_querier, mock_git_effector)

            # Act.
            result = manager.get_git_tags()

            # Assert.
            result == ["tag1", "tag2"]

    class Test_get_commit_messages:
        def test_with_valid_hash_returns_list_of_messages(self):
            # Arrange.
            mock_git_querier = MagicMock()
            mock_git_effector = MagicMock()
            manager = GitManager(DEFAULT_CONFIG, mock_git_querier, mock_git_effector)

            # Act.
            manager.get_commit_messages_since("HEAD~2")

            # Assert.
            mock_git_querier.get_commits.assert_called_with("HEAD~2")

    class Test_apply_tag:
        @patch("subprocess.run")
        def test_with_existing_tag_does_nothing(self, mock_run):
            # Arrange.
            existing_tags = ["v0.1.0", "v3.0.0", "v2.0.0"]
            new_tag = "v3.0.0"
            mock_git_querier = MagicMock()
            mock_git_effector = MagicMock()
            manager = GitManager(DEFAULT_CONFIG, mock_git_querier, mock_git_effector)

            # Act.
            manager.apply_tag(existing_tags, new_tag)

            # Assert.
            mock_git_querier._effector.set_config_item.assert_not_called()

        @patch("os.system")
        def test_with_new_tag_tags_and_pushes(self, mock_system):
            # Arrange.
            existing_tags = ["v0.1.0", "v3.0.0", "v2.0.0"]
            new_tag = Tag("v4.0.0", 4, 0, 0)
            mock_system.return_value = 0  # exit code
            mock_git_querier = MagicMock()
            mock_git_effector = MagicMock()
            manager = GitManager(DEFAULT_CONFIG, mock_git_querier, mock_git_effector)
            local_git_options = LocalGitOptions(
                name="original",
                email="original@email.com",
                remote="git@repo:user/project.git",
            )
            mock_get_existing_git_info = patch.object(
                manager, "get_existing_git_info", return_value=local_git_options
            )
            mock_get_existing_git_info.start()

            # Act.
            manager.apply_tag(existing_tags, new_tag)

            # Assert.
            mock_git_effector.set_config_item.assert_has_calls([
                call("user.email", "semver@pagekey.io"),
                call("user.name", "PageKey Semver"),
                call("user.email", "original@email.com"),
                call("user.name", "original"),
                call("remote.origin.url", "git@repo:user/project.git"),
            ])
            mock_git_effector.add_all.assert_called_once()
            mock_git_effector.create_commit.assert_called_with(new_tag.name)
            mock_git_effector.create_tag.assert_called_with(new_tag.name)
            mock_get_existing_git_info.stop()

        @patch("os.system")
        def test_with_config_applies_config_name_email(self, mock_system):
            existing_tags = ["v0.1.0", "v3.0.0", "v2.0.0"]
            new_tag = Tag("v4.0.0", 4, 0, 0)
            mock_system.return_value = 0  # exit code
            config = SemverConfig(
                changelog_path="CHANGELOG.md",
                changelog_writer="pagekey_semver.changelog_writer:ChangelogWriter",
                format="v%M.%m.%p",
                git=GitConfig(
                    name="some name",
                    email="some@email.com",
                ),
                prefixes=[],
                replace_files=[],
            )
            mock_git_querier = MagicMock()
            mock_git_effector = MagicMock()
            manager = GitManager(config, mock_git_querier, mock_git_effector)

            # Act.
            manager.apply_tag(existing_tags, new_tag)

            # Assert.
            mock_git_effector.set_config_item.assert_has_calls([
                call("user.email", "some@email.com"),
                call("user.name", "some name"),
            ])
