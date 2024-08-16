"""Test GitHub integration module."""


from pagekey_semver.integrations.release_creator.base import CreateReleaseConfig
from pagekey_semver.integrations.release_creator.github import GitHubReleaseCreator
from pagekey_semver.models import Tag


class TestGitHubReleaseCreator:
    class Test_create_release:
        def test_with_successful_request_makes_request(self):
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
