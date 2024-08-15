from pydantic import BaseModel


class GitHubReleaseConfig(BaseModel):
    """Config for creating GitHub releases."""

    enabled: bool


class GitHubIntegrationConfig(BaseModel):
    """Configuration for any GitHub-specific integrations."""

    create_release: GitHubReleaseConfig = GitHubReleaseConfig(enabled=False)
