import abc

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
