"""Test GitHub integration module."""

from unittest.mock import patch
from pagekey_semver.integrations.release_creator import (
    CreateReleaseConfig,
    GitHubReleaseCreator,
    GitLabReleaseCreator,
)
from pagekey_semver.models import Tag


MODULE_UNDER_TEST = "pagekey_semver.integrations.release_creator"


class TestGitHubReleaseCreator:
    class Test_create_release:
        @patch(f"{MODULE_UNDER_TEST}.os")
        @patch(f"{MODULE_UNDER_TEST}.requests")
        def test_with_successful_request_makes_request(self, mock_requests, mock_os):
            # Arrange.
            config = CreateReleaseConfig(
                project="me/project",
                token_variable="GITHUB_TOKEN",
                title_format="Version %M.%m.%p",
                body="Here is yet another release.",
            )
            tag = Tag("v1.0.0", 1, 0, 0)
            creator = GitHubReleaseCreator()
            mock_os.getenv.side_effect = ["my-github-token"]

            # Act.
            creator.create_release(config, tag)

            # Assert.
            mock_os.getenv.assert_called_with("GITHUB_TOKEN", "")
            mock_requests.post.assert_called_with(
                "https://api.github.com/repos/me/project/releases",
                json={
                    "tag_name": "v1.0.0",
                    "name": "Version 1.0.0",
                    "body": "Here is yet another release.",
                    "draft": False,
                    "prerelease": False,
                },
                headers={
                    "Authorization": "token my-github-token",
                    "Content-Type": "application/json",
                },
            )


class TestGitLabReleaseCreator:
    class Test_create_release:
        @patch(f"{MODULE_UNDER_TEST}.os")
        @patch(f"{MODULE_UNDER_TEST}.requests")
        def test_with_successful_request_makes_request(self, mock_requests, mock_os):
            # Arrange.
            config = CreateReleaseConfig(
                project="1234",
                token_variable="GITLAB_TOKEN",
                title_format="Version %M.%m.%p",
                body="Here is yet another release.",
            )
            tag = Tag("v1.0.0", 1, 0, 0)
            creator = GitLabReleaseCreator()
            mock_os.getenv.side_effect = ["my-gitlab-token"]

            # Act.
            creator.create_release(config, tag)

            # Assert.
            mock_os.getenv.assert_called_with("GITLAB_TOKEN")
            mock_requests.post.assert_called_with(
                "https://gitlab.com/api/v4/projects/1234/releases",
                json={
                    "tag_name": "v1.0.0",
                    "name": "Version 1.0.0",
                    "description": "Here is yet another release.",
                    "ref": "v1.0.0",
                },
                headers={
                    "PRIVATE-TOKEN": "my-gitlab-token",
                    "Content-Type": "application/json",
                },
            )
