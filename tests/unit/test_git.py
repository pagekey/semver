"""Test Git module."""

from unittest.mock import MagicMock, call, patch

from pagekey_semver.config import DEFAULT_CONFIG
from pagekey_semver.models import GitConfig, SemverConfig
from pagekey_semver.git.manager import GitManager, LocalGitOptions
from pagekey_semver.release import Tag


MODULE_UNDER_TEST = "pagekey_semver.git.manager"


class TestGitManager:
    class Test_get_existing_git_info:
        @patch("subprocess.run")
        def test_with_successful_call_returns_gitconfig(self, mock_run):
            # Arrange.
            mock_result_email = MagicMock()
            mock_result_email.stdout = "email@email.com\n"
            mock_result_name = MagicMock()
            mock_result_name.stdout = "me\n"
            mock_result_remote = MagicMock()
            mock_result_remote.stdout = "some_remote\n"
            mock_run.side_effect = [
                mock_result_email,
                mock_result_name,
                mock_result_remote,
            ]
            manager = GitManager(DEFAULT_CONFIG)

            # Act.
            result = manager.get_existing_git_info()

            # Assert.
            mock_run.assert_has_calls(
                [
                    call(
                        "git config user.email".split(),
                        check=True,
                        stdout=-1,
                        stderr=-1,
                        text=True,
                    ),
                    call(
                        "git config user.name".split(),
                        check=True,
                        stdout=-1,
                        stderr=-1,
                        text=True,
                    ),
                    call(
                        "git config remote.origin.url".split(),
                        check=True,
                        stdout=-1,
                        stderr=-1,
                        text=True,
                    ),
                ]
            )
            assert result.email == "email@email.com"
            assert result.name == "me"
            assert result.remote == "some_remote"

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
            manager.apply_tag(existing_tags, new_tag)

            # Assert.
            mock_run.assert_not_called()

        @patch("os.system")
        def test_with_new_tag_tags_and_pushes(self, mock_system):
            # Arrange.
            existing_tags = ["v0.1.0", "v3.0.0", "v2.0.0"]
            new_tag = Tag("v4.0.0", 4, 0, 0)
            mock_system.return_value = 0  # exit code
            manager = GitManager(DEFAULT_CONFIG)
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
            commands = [
                f'git config user.email "semver@pagekey.io"',
                f'git config user.name "PageKey Semver"',
                f"git add --all",
                f"git commit -m '{new_tag.name}'",
                f"git tag {new_tag.name}",
                f"git push origin {new_tag.name}",
                f"git push origin HEAD",
                f'git config user.email "original@email.com"',
                f'git config user.name "original"',
                f'git config remote.origin.url "git@repo:user/project.git"',
            ]
            mock_system.assert_has_calls([call(command) for command in commands])
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
            manager = GitManager(config)

            # Act.
            manager.apply_tag(existing_tags, new_tag)

            # Assert.
            mock_system.assert_has_calls(
                [
                    call('git config user.email "some@email.com"'),
                    call('git config user.name "some name"'),
                ]
            )
