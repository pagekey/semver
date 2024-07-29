"""Test changelog module."""
from unittest.mock import call, mock_open, patch
from pagekey_semver.changelog import ChangelogWriter
from pagekey_semver.release import Commit


MODULE_UNDER_TEST = "pagekey_semver.changelog"

class TestChangelogWriter:
    @patch('builtins.open', new_callable=mock_open)
    def test_update_changelog_with_commits_updates_changelog_file(self, mock_open):
        # Arrange.
        version = "v1.0.0"
        commits = [
            Commit(hash="aaaaa1", message="my commit"),
            Commit(hash="aaaaa2", message="fix: Do something somewhat important"),
            Commit(hash="aaaaa3", message="feat: Add something"),
            Commit(hash="aaaaa4", message="random commit"),
            Commit(hash="aaaaa5", message="major: Wow this is a big deal"),
            Commit(hash="aaaaa6", message="some other commit"),
        ]
        mock_file = mock_open.return_value
        writer = ChangelogWriter()

        # Act.
        writer.update_changelog(version, commits)

        # Assert.
        mock_open.assert_called_with("CHANGELOG.md", "a")
        mock_file.write.assert_has_calls([
            call(f"## {version}\n\n"),
            call("- fix: Do something somewhat important (aaaaa2)\n"),
            call("- feat: Add something (aaaaa3)\n"),
            call("- major: Wow this is a big deal (aaaaa5)\n"),
            call("\n"),
        ])
