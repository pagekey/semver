from typing import Literal

from pagekey_semver.models import Tag
from pagekey_semver.replace_file.base import ReplaceFile, ReplaceFileType


class JsonReplaceFile(ReplaceFile):
    """Represents JSON file to replaced on new release."""

    type: Literal[ReplaceFileType.JSON] = ReplaceFileType.JSON
    key: str
    format: str

    def perform_replace(self, tag: Tag) -> str:
        """Replace a key in a JSON file using the provided format.

        Args:
            tag: Version tag to replace key with.
        """
