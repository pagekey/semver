"""Test GitHub integration module."""


from unittest.mock import patch
from pagekey_semver.integrations.release_creator import CreateReleaseConfig, GitHubReleaseCreator
from pagekey_semver.models import Tag


MODULE_UNDER_TEST = "pagekey_semver.integrations.release_creator"


class TestGitHubReleaseCreator:
    class Test_create_release:

        @patch(f"{MODULE_UNDER_TEST}.requests")
        def test_with_successful_request_makes_request(self, mock_requests):
            # Arrange.
            config = CreateReleaseConfig(
                project="me/project",
                token_variable="GITHUB_TOKEN",
                title_format="Version %M.%m.%p",
                body="Here is yet another release."
            )
            tag = Tag("v1.0.0", 1, 0, 0)
            creator = GitHubReleaseCreator()
            
            # Act.
            creator.create_release(config, tag)
            
            # Assert.
            pass


class TestGitLabReleaseCreator:
    class Test_create_release:
        def test_with_successful_request_makes_request(self):
            pass

