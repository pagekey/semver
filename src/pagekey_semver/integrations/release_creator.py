import abc
import requests
from typing import Optional

from pydantic import BaseModel

from pagekey_semver.models import Tag


class CreateReleaseConfig(BaseModel):
    """."""

    project: str
    token_variable: str
    title_format: str
    body: str


class ReleaseCreator(abc.ABC):
    """Create a release on a Git hosting platform (GitHub, GitLab)."""

    def create_release(self, release_config: CreateReleaseConfig, tag: Tag):
        """."""

class GitHubIntegrationConfig(BaseModel):
    """Configuration for any GitHub-specific integrations."""

    create_release: Optional[CreateReleaseConfig] = None

class GitLabIntegrationConfig(BaseModel):
    """Configuration for any GitLab-specific integrations."""

    create_release: Optional[CreateReleaseConfig] = None

class GitHubReleaseCreator(ReleaseCreator):
    def create_release(self, release_config: CreateReleaseConfig, tag: Tag):
        pass
