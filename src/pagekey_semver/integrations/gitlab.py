from typing import Optional
from pydantic import BaseModel

from pagekey_semver.integrations.release_creator import CreateReleaseConfig


class GitLabIntegrationConfig(BaseModel):
    """Configuration for any GitLab-specific integrations."""

    create_release: Optional[CreateReleaseConfig] = None
