from typing import Optional
from pydantic import BaseModel

from pagekey_semver.integrations.release_creator import CreateReleaseConfig


class GitHubIntegrationConfig(BaseModel):
    """Configuration for any GitHub-specific integrations."""

    create_release: Optional[CreateReleaseConfig] = None
