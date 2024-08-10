import json
from typing import Literal

from pagekey_semver.models import Tag
from pagekey_semver.file_replacer.base import FileReplacer, FileReplacerType
from pagekey_semver.util.update_dict import set_dict_value


class JsonFileReplacer(FileReplacer):
    """Represents JSON file to replaced on new release."""

    type: Literal[FileReplacerType.JSON] = FileReplacerType.JSON
    key: str
    format: str

    def perform_replace(self, tag: Tag) -> str:
        """Replace a key in a JSON file using the provided format.

        Args:
            tag: Version tag to replace key with.
        """
        # Read the file.
        with open(self.name, "r") as file_handle:
            contents = json.load(file_handle)

        # Compute the value based on format and tag.
        new_version_str = (
            self.format.replace("%M", str(tag.major))
            .replace("%m", str(tag.minor))
            .replace("%p", str(tag.patch))
        )
        # Replace the key with the computed value.
        set_dict_value(contents, self.key, new_version_str)

        # Write the new file contents back to the same file.
        with open(self.name, "w") as file_handle:
            json.dump(contents, file_handle)
