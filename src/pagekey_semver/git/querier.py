"""Module for querying Git."""


import abc
from typing import List, Optional


class GitQuerier(abc.ABC):
    """Query the current Git repo for data."""

    @abc.abstractmethod
    def get_config_item(self, key: str) -> str:
        """Get the Git config stored for the provided key.
        
        Args:
            key: Config key to retrieve.
        
        Returns:
            The value of the config key.
        """

    @abc.abstractmethod
    def get_tag_names(self) -> List[str]:
        """Get a list of all Git tag names for the current repo.

        Returns:
            List of each tag name as a string.
        """

    @abc.abstractmethod
    def get_commits(self, since_ref: Optional[str] = None) -> List[str]:
        """Return commits in this repo since provided ref, or all commits.

        Args:
            since_ref: Reference to a commit to pull messages since, or None.

        Returns:
            Commits since `commit_hash` if provided.
            All commits if `commit_hash` is None.
        """
