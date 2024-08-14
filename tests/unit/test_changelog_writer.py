"""Test changelog module."""

from unittest.mock import call, mock_open, patch
from pagekey_semver.changelog_writer import ChangelogWriter, DefaultChangelogWriter
from pagekey_semver.config import DEFAULT_CONFIG, DEFAULT_CONFIG_DICT
from pagekey_semver.config import SemverConfig
from pagekey_semver.models import Commit, Tag


MODULE_UNDER_TEST = "pagekey_semver.changelog_writer"


class TestChangelogWriter:
    @patch(f"{MODULE_UNDER_TEST}.dynamic_import")
    def test_from_config_calls_dynamic_import(self, mock_dynamic_import):
        # Arrange.
        config = DEFAULT_CONFIG
        imported_class = mock_dynamic_import.return_value

        # Act.
        result = ChangelogWriter.from_config(config)

        # Assert.
        mock_dynamic_import.assert_called_with(config.changelog_writer)
        imported_class.assert_called_with(config)
        assert result == imported_class.return_value


class TestDefaultChangelogWriter:
    @patch(f"{MODULE_UNDER_TEST}.os")
    @patch(f"{MODULE_UNDER_TEST}.tempfile.NamedTemporaryFile", new_callable=mock_open)
    @patch("builtins.open", new_callable=mock_open)
    def test_update_changelog_with_commits_updates_changelog_file(
        self, mock_open, mock_tempfile, mock_os
    ):
        # Arrange.
        version = Tag("v1.0.0", 1, 0, 0)
        commits = [
            Commit(hash="aaaaa1", message="my commit"),
            Commit(hash="aaaaa2", message="fix: Do something somewhat important"),
            Commit(hash="aaaaa3", message="feat: Add something"),
            Commit(hash="aaaaa4", message="random commit"),
            Commit(hash="aaaaa5", message="major: Wow this is a big deal"),
            Commit(hash="aaaaa6", message="some other commit"),
        ]
        mock_file = mock_tempfile.return_value
        config = SemverConfig(
            **{**DEFAULT_CONFIG_DICT, "changelog_path": "docs/CHANGELOG.md"}
        )
        writer = DefaultChangelogWriter(config)

        # Act.
        writer.update_changelog(version, commits)

        # Assert.
        mock_open.assert_called_with("docs/CHANGELOG.md", "w")
        mock_file.write.assert_has_calls(
            [
                call(f"## {version.name}\n\n"),
                call("- fix: Do something somewhat important (aaaaa2)\n"),
                call("- feat: Add something (aaaaa3)\n"),
                call("- major: Wow this is a big deal (aaaaa5)\n"),
                call("\n"),
            ]
        )
