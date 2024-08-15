from pydantic import BaseModel


class GitLabReleaseConfig(BaseModel):
    """Config for creating GitLab releases."""

    enabled: bool


class GitLabIntegrationConfig(BaseModel):
    """Configuration for any GitLab-specific integrations."""

    create_release: GitLabReleaseConfig = GitLabReleaseConfig(enabled=False)
