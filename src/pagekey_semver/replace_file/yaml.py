from typing import Literal

from pagekey_semver.models import Tag
from pagekey_semver.replace_file.base import ReplaceFile, ReplaceFileType


class YamlReplaceFile(ReplaceFile):
    """Represents YAML file to replaced on new release."""

    type: Literal[ReplaceFileType.YAML] = ReplaceFileType.YAML
    key: str
    format: str

    def perform_replace(self, tag: Tag) -> str:
        """Replace a key in a YAML file using the provided format.

        Args:
            tag: Version tag to replace key with.
        """
