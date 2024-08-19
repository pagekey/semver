"""Module for interacting with Git."""

import os
from dataclasses import dataclass
import re
from typing import List, Optional
from pagekey_semver.git.effector import CommandGitEffector, GitEffector
from pagekey_semver.git.querier import CommandGitQuerier, GitQuerier
from pagekey_semver.config import SemverConfig
from pagekey_semver.models import Commit, Tag


@dataclass
class LocalGitOptions:
    """Any Git options that will be changes by this package."""

    name: str
    email: str
    remote: str


class GitManagerException(Exception):
    """Exception managing Git."""


class GitManager:
    """Class to handle all communications with Git executable."""

    def __init__(
        self,
        config: SemverConfig,
        querier: GitQuerier = CommandGitQuerier(),
        effector: GitEffector = CommandGitEffector(),
    ):
        """Initialize Git manager."""
        self._config = config
        self._querier = querier
        self._effector = effector

    def get_existing_git_info(self) -> LocalGitOptions:
        """Determine exisitng Git config information.

        This will allow the original configuration to be restored after run,
        which is important to avoid messing up the user's configuration when
        running locally.

        Returns:
            LocalGitOptions representing any Git options that may get changed.

        Raises:
            CalledProcessError if there is an issue calling Git to check these values.
        """
        return LocalGitOptions(
            name=self._querier.get_config_item("user.name"),
            email=self._querier.get_config_item("user.email"),
            remote=self._querier.get_config_item("remote.origin.url"),
        )

    def get_git_tags(self) -> List[str]:
        """Get a list of all Git tags for the current repo.

        Returns:
            List of each tag name as a string.
        """
        return self._querier.get_tag_names()

    def get_commit_messages_since(self, commit_hash: Optional[str]) -> List[Commit]:
        """Return a  list of commit messages since a commit ref.

        Args:
            commit_hash: Reference to a commit to pull messages since, or None.

        Returns:
            Commit messages since `commit_hash` if provided.
            All commit messages if `commit_hash` is None.
        """
        return self._querier.get_commits(commit_hash)

    def apply_tag(self, existing_tags: List[Tag], new_tag: Tag) -> None:
        """Commit, tag, and push.

        Changes Git username, email based on config
        and restores them to what they were previously when done.

        Args:
            existing_tags: List of pre-existing Git tags in repo.
            new_tag: Tag to be added, if it does not already exist.
        """
        if new_tag not in existing_tags:
            # Check out branch on GitLab
            gitlab_branch = os.getenv("CI_COMMIT_BRANCH", "")
            if len(gitlab_branch) > 0:
                print(f"Checking out CI_COMMIT_BRANCH={gitlab_branch}")
                self._effector.checkout(gitlab_branch)

            print(f"Tagging/pushing new tag: {new_tag}", flush=True)
            original_git_config = self.get_existing_git_info()

            self.set_git_remote()
            self._effector.set_config_item("user.email", self._config.git.email)
            self._effector.set_config_item("user.name", self._config.git.name)
            self._effector.add_all()
            self._effector.create_commit(new_tag.name)
            self._effector.create_tag(new_tag.name)
            self._effector.push("origin", new_tag.name)
            self._effector.push("origin", "HEAD")
            # Restore original Git config
            if len(original_git_config.email) > 0:
                self._effector.set_config_item("user.email", original_git_config.email)
            if len(original_git_config.email) > 0:
                self._effector.set_config_item("user.name", original_git_config.name)
            if len(original_git_config.email) > 0:
                self._effector.set_config_item(
                    "remote.origin.url", original_git_config.remote
                )
        else:
            print(f"Tag {new_tag} already exists - skipping tag/push.", flush=True)

    def set_git_remote(self) -> None:
        """Set push remote based on SEMVER_USER and SEMVER_TOKEN env vars."""
        user = os.getenv("SEMVER_USER", "")
        token = os.getenv("SEMVER_TOKEN", "")
        if len(user) > 0 and len(token) > 0:
            existing_remote = self._querier.get_config_item("remote.origin.url")
            if existing_remote.startswith("git@"):
                # Replace SSH url.
                new_remote = existing_remote.replace(":", "/").replace(
                    "git@", f"https://{user}:{token}@"
                )
            elif existing_remote.startswith("https://"):
                HTTPS_WITH_CREDENTIALS_PATTERN = r"https\://[^:@]+:[^:@]+@"
                if re.search(HTTPS_WITH_CREDENTIALS_PATTERN, existing_remote):
                    # Replace HTTPS with existing auth.
                    new_remote = re.sub(
                        HTTPS_WITH_CREDENTIALS_PATTERN,
                        f"https://{user}:{token}@",
                        existing_remote,
                    )
                else:
                    # Add auth to HTTPS without any credentials.
                    new_remote = existing_remote.replace(
                        "https://", f"https://{user}:{token}@"
                    )
            else:
                raise GitManagerException(
                    f"Unsupported remote URL format: {existing_remote}"
                )
            # Set the new remote.
            self._effector.set_config_item("remote.origin.url", new_remote)
        else:
            print(
                "Warning: SEMVER_USER and/or SEMVER_TOKEN not defined. Consider defining them for push authorization."
            )
