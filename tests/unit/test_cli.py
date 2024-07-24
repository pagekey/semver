"""Test CLI module."""
from unittest.mock import patch
from pagekey_semver.cli import cli_entrypoint
from pagekey_semver.release import ReleaseType


MODULE_UNDER_TEST = "pagekey_semver.cli"


@patch(f"{MODULE_UNDER_TEST}.apply_tag")
@patch(f"{MODULE_UNDER_TEST}.update_changelog")
@patch(f"{MODULE_UNDER_TEST}.compute_next_version")
@patch(f"{MODULE_UNDER_TEST}.compute_release_type")
@patch(f"{MODULE_UNDER_TEST}.get_commit_messages_since")
@patch(f"{MODULE_UNDER_TEST}.get_biggest_tag")
@patch(f"{MODULE_UNDER_TEST}.get_git_tags")
def test_cli_entrypoint_with_no_args_calls_all_functions(
    mock_get_git_tags,
    mock_get_biggest_tag,
    mock_get_commit_messages_since,
    mock_compute_release_type,
    mock_compute_next_version,
    mock_update_changelog,
    mock_apply_tag,
):
    # Arrange.
    tags = ["v1.0.0", "v3.0.0", "v2.0.0"]
    mock_get_git_tags.return_value = tags
    biggest_tag = "v3.0.0"
    mock_get_biggest_tag.return_value = biggest_tag
    commits = ["fix: Message 1", "feat: Message 2"]
    mock_get_commit_messages_since.return_value = commits
    release_type = ReleaseType.MINOR
    mock_compute_release_type.return_value = release_type
    next_version = "v3.1.0"
    mock_compute_next_version.return_value = next_version
    # Act.
    cli_entrypoint()
    # Assert.
    mock_get_git_tags.assert_called_once()
    mock_get_biggest_tag.assert_called_with(tags)
    mock_get_commit_messages_since.assert_called_with("v3.0.0")
    mock_compute_release_type.assert_called_with(commits)
    mock_compute_next_version.assert_called_with(release_type, tags)
    mock_update_changelog.assert_called_with(next_version, commits)
    mock_apply_tag.assert_called_with(tags, next_version)


@patch(f"{MODULE_UNDER_TEST}.apply_tag")
@patch(f"{MODULE_UNDER_TEST}.update_changelog")
@patch(f"{MODULE_UNDER_TEST}.compute_next_version")
@patch(f"{MODULE_UNDER_TEST}.compute_release_type")
@patch(f"{MODULE_UNDER_TEST}.get_commit_messages_since")
@patch(f"{MODULE_UNDER_TEST}.get_biggest_tag")
@patch(f"{MODULE_UNDER_TEST}.get_git_tags")
def test_cli_entrypoint_with_dry_run_does_not_push(
    mock_get_git_tags,
    mock_get_biggest_tag,
    mock_get_commit_messages_since,
    mock_compute_release_type,
    mock_compute_next_version,
    mock_update_changelog,
    mock_apply_tag,
):
    # Arrange.
    tags = ["v1.0.0", "v3.0.0", "v2.0.0"]
    mock_get_git_tags.return_value = tags
    biggest_tag = "v3.0.0"
    mock_get_biggest_tag.return_value = biggest_tag
    commits = ["fix: Message 1", "feat: Message 2"]
    mock_get_commit_messages_since.return_value = commits
    release_type = ReleaseType.MINOR
    mock_compute_release_type.return_value = release_type
    next_version = "v3.1.0"
    mock_compute_next_version.return_value = next_version
    # Act.
    cli_entrypoint(["--dry-run"])
    # Assert.
    mock_get_git_tags.assert_called_once()
    mock_get_biggest_tag.assert_called_with(tags)
    mock_get_commit_messages_since.assert_called_with("v3.0.0")
    mock_compute_release_type.assert_called_with(commits)
    mock_compute_next_version.assert_called_with(release_type, tags)
    mock_update_changelog.assert_called_with(next_version, commits)
    mock_apply_tag.assert_not_called()
