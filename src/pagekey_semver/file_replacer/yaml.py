from typing import Literal

import yaml

from pagekey_semver.models import Tag
from pagekey_semver.file_replacer.base import FileReplacer, FileReplacerType
from pagekey_semver.util.update_dict import set_dict_value


class YamlFileReplacer(FileReplacer):
    """Represents YAML file to replaced on new release."""

    type: Literal[FileReplacerType.YAML] = FileReplacerType.YAML
    key: str
    format: str

    def perform_replace(self, tag: Tag) -> str:
        """Replace a key in a YAML file using the provided format.

        Args:
            tag: Version tag to replace key with.
        """
        # Read the file.
        with open(self.name, "r") as file_handle:
            contents = yaml.safe_load(file_handle)

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
            yaml.dump(contents, file_handle)
