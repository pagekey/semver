from typing import Literal

from pagekey_semver.models import Tag
from pagekey_semver.replace_file.base import ReplaceFile, ReplaceFileType


class SedReplaceFile(ReplaceFile):
    """Represents a file to replaced using `sed` on new release."""

    type: Literal[ReplaceFileType.SED] = ReplaceFileType.SED
    script: str

    def perform_replace(self, tag: Tag) -> str:
        """Run the sed program to replace a tag in a file.

        Args:
            script: Sed script to run on the file.
        """
