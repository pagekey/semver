"""Test CLI module."""

from pathlib import Path
from unittest.mock import patch
from pagekey_semver.cli import cli_entrypoint
from pagekey_semver.models import ReleaseType, Tag


MODULE_UNDER_TEST = "pagekey_semver.cli"


@patch(f"{MODULE_UNDER_TEST}.ChangelogWriter")
@patch(f"{MODULE_UNDER_TEST}.FileReplacer")
@patch(f"{MODULE_UNDER_TEST}.GitManager")
@patch(f"{MODULE_UNDER_TEST}.SemverRelease")
@patch(f"{MODULE_UNDER_TEST}.load_config")
def test_cli_entrypoint_with_no_args_calls_all_functions(
    mock_load_config,
    mock_release_cls,
    mock_git_manager_cls,
    mock_file_replacer_cls,
    mock_changelog_writer_cls,
):
    # Arrange.
    config = mock_load_config.return_value
    tags = ["v1.0.0", "v3.0.0", "v2.0.0"]
    mock_git_manager = mock_git_manager_cls.return_value
    mock_git_manager.get_git_tags.return_value = tags
    biggest_tag = Tag("v3.0.0", 3, 0, 0)
    mock_release = mock_release_cls.return_value
    mock_release.get_biggest_tag.return_value = biggest_tag
    commits = ["fix: Message 1", "feat: Message 2"]
    mock_git_manager.get_commit_messages_since.return_value = commits
    release_type = ReleaseType.MINOR
    mock_release.compute_release_type.return_value = release_type
    next_version = "v3.1.0"
    mock_release.compute_next_version.return_value = next_version
    mock_changelog_writer = mock_changelog_writer_cls.from_config.return_value
    mock_file_replacer = mock_file_replacer_cls.return_value

    # Act.
    cli_entrypoint(["apply"])

    # Assert.
    mock_git_manager_cls.assert_called_with(config)
    mock_changelog_writer_cls.from_config.assert_called_with(config)
    mock_release_cls.assert_called_with(config)
    mock_load_config.assert_called_with(Path(".semver"))
    mock_git_manager.get_git_tags.assert_called_once()
    mock_release.get_biggest_tag.assert_called_with(tags)
    mock_git_manager.get_commit_messages_since.assert_called_with("v3.0.0")
    mock_release.compute_release_type.assert_called_with(commits)
    mock_release.compute_next_version.assert_called_with(release_type, tags)
    mock_changelog_writer.update_changelog.assert_called_with(next_version, commits)
    mock_git_manager.apply_tag.assert_called_with(tags, next_version)
    mock_file_replacer_cls.assert_called_with(config, next_version)
    mock_file_replacer.replace_all.assert_called_with()


@patch(f"{MODULE_UNDER_TEST}.ChangelogWriter")
@patch(f"{MODULE_UNDER_TEST}.FileReplacer")
@patch(f"{MODULE_UNDER_TEST}.GitManager")
@patch(f"{MODULE_UNDER_TEST}.SemverRelease")
@patch(f"{MODULE_UNDER_TEST}.load_config")
def test_cli_entrypoint_with_dry_run_does_not_push(
    mock_load_config,
    mock_release_cls,
    mock_git_manager_cls,
    mock_file_replacer_cls,
    mock_changelog_writer_cls,
):
    # Arrange.
    config = mock_load_config.return_value
    tags = ["v1.0.0", "v3.0.0", "v2.0.0"]
    mock_git_manager = mock_git_manager_cls.return_value
    mock_git_manager.get_git_tags.return_value = tags
    biggest_tag = Tag("v3.0.0", 3, 0, 0)
    mock_release = mock_release_cls.return_value
    mock_release.get_biggest_tag.return_value = biggest_tag
    commits = ["fix: Message 1", "feat: Message 2"]
    mock_git_manager.get_commit_messages_since.return_value = commits
    release_type = ReleaseType.MINOR
    mock_release.compute_release_type.return_value = release_type
    next_version = "v3.1.0"
    mock_release.compute_next_version.return_value = next_version
    mock_changelog_writer = mock_changelog_writer_cls.from_config.return_value

    # Act.
    cli_entrypoint(["plan"])

    # Assert.
    mock_git_manager_cls.assert_called_with(config)
    mock_changelog_writer_cls.from_config.assert_called_with(config)
    mock_release_cls.assert_called_with(config)
    mock_load_config.assert_called_with(Path(".semver"))
    mock_git_manager.get_git_tags.assert_called_once()
    mock_release.get_biggest_tag.assert_called_with(tags)
    mock_git_manager.get_commit_messages_since.assert_called_with("v3.0.0")
    mock_release.compute_release_type.assert_called_with(commits)
    mock_release.compute_next_version.assert_called_with(release_type, tags)
    mock_changelog_writer.update_changelog.assert_not_called()
    mock_git_manager.apply_tag.assert_not_called()
    mock_file_replacer_cls.assert_not_called()
