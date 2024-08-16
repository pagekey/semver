from typing import Optional
from pydantic import BaseModel

from pagekey_semver.integrations.release_creator.base import CreateReleaseConfig, ReleaseCreator
from pagekey_semver.models import Tag


class GitHubIntegrationConfig(BaseModel):
    """Configuration for any GitHub-specific integrations."""

    create_release: Optional[CreateReleaseConfig] = None

class GitHubReleaseCreator(ReleaseCreator):
    def create_release(self, release_config: CreateReleaseConfig, tag: Tag):
        pass
