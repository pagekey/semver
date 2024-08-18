import abc
import os
from typing import Optional

import requests
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
        token = os.getenv("GITHUB_TOKEN")
        release_title = (
            release_config.title_format.replace("%M", str(tag.major))
            .replace("%m", str(tag.minor))
            .replace("%p", str(tag.patch))
        )
        print("POSTing GitHub release")
        request = requests.post(
            f"https://api.github.com/repos/{release_config.project}/releases",
            json={
                "tag_name": tag.name,
                "name": release_title,
                "body": release_config.body,
                "draft": False,
                "prerelease": False,
            },
            headers={
                "Authorization": f"token {token}",
                "Accept": "application/bnd.github.v3+json",
            },
        )
        print(f"Status: {request.status_code}")
        print(f"Body: {request.content.decode()}")


class GitLabReleaseCreator(ReleaseCreator):
    def create_release(self, release_config: CreateReleaseConfig, tag: Tag):
        token = os.getenv("GITLAB_TOKEN")
        release_title = (
            release_config.title_format.replace("%M", str(tag.major))
            .replace("%m", str(tag.minor))
            .replace("%p", str(tag.patch))
        )
        print("POSTing GitLab release")
        request = requests.post(
            f"https://gitlab.com/api/v4/projects/{release_config.project}/releases",
            json={
                "tag_name": tag.name,
                "name": release_title,
                "description": release_config.body,
                "ref": tag.name,
            },
            headers={
                "PRIVATE-TOKEN": token,
                "Content-Type": "application/json",
            },
        )
        print(f"Status: {request.status_code}")
        print(f"Body: {request.content.decode()}")
