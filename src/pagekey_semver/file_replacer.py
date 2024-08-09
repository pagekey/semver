"""Module for file replacer."""

import json
import os
import shutil
import toml
import yaml
from pagekey_semver.models import (
    JsonReplaceFile,
    ReplaceFileType,
    ReplaceFileUnion,
    SedReplaceFile,
    SemverConfig,
    TomlReplaceFile,
    YamlReplaceFile,
)
from pagekey_semver.release import Tag
from pagekey_semver.util.update_dict import set_dict_value


class FileReplacer:
    """Class to handle replacing files on new release."""

    def __init__(self, config: SemverConfig, new_version: Tag) -> None:
        """Initialize file replacer.
        
        Args:
            config: Settings for semver application.
            new_version: Latest version to replace file values with.
        """
        self._config = config
        self._new_version = new_version

    def replace_all(self) -> None:
        """Replace every file specified in config."""
        for replace_file in self._config.replace_files:
            self.replace_one(replace_file)

    def replace_one(self, file: ReplaceFileUnion) -> None:
        """Given a ReplaceFile, perform replace based on its type."""
        if file.type == ReplaceFileType.JSON:
            self.replace_json(file)
        elif file.type == ReplaceFileType.SED:
            self.replace_sed(file)
        elif file.type == ReplaceFileType.TOML:
            self.replace_toml(file)
        else:
            self.replace_yaml(file)

    def replace_json(self, replace_file: JsonReplaceFile) -> None:
        """Replace a JSON file's key with the new_version's name.
        
        Parses to JSON file into a dict, replaces the key,
        and dumps the result back into the original file.
        """
        with open(replace_file.name, "r") as replace_file_handle:
            contents = json.load(replace_file_handle)

        set_dict_value(contents, replace_file.key, self._new_version.name)

        with open(replace_file.name, "w") as replace_file_handle:
            json.dump(contents, replace_file_handle)

    def replace_sed(self, replace_file: SedReplaceFile):
        """Use sed to make an arbitrary replacement based on new version.
        
        Replaces %M/%m/%p with new_version's major/minor/patch,
        then calls sed with the provided `script`.
        """
        if shutil.which("sed") is None:
            raise EnvironmentError(
                "Sed executable not found on system - have you installed sed?"
            )
        script_escaped = replace_file.script.replace("'", "\\'")
        script_replaced = (
            script_escaped.replace("%M", str(self._new_version.major))
            .replace("%m", str(self._new_version.minor))
            .replace("%p", str(self._new_version.patch))
        )
        exit_code = os.system(f"sed -i '{script_replaced}' {replace_file.name}")
        if exit_code != 0:
            raise OSError("Invoking sed failed!")

    def replace_toml(self, replace_file: TomlReplaceFile):
        """Replace a TOML file's key with the new_version's name.
        
        Parses to TOML file into a dict, replaces the key,
        and dumps the result back into the original file.
        """
        with open(replace_file.name, "r") as replace_file_handle:
            contents = toml.load(replace_file_handle)

        set_dict_value(contents, replace_file.key, self._new_version.name)

        with open(replace_file.name, "w") as replace_file_handle:
            toml.dump(contents, replace_file_handle)

    def replace_yaml(self, replace_file: YamlReplaceFile):
        """Replace a YAML file's key with the new_version's name.
        
        Parses to YAML file into a dict, replaces the key,
        and dumps the result back into the original file.
        """
        with open(replace_file.name, "r") as replace_file_handle:
            contents = yaml.safe_load(replace_file_handle)

        set_dict_value(contents, replace_file.key, self._new_version.name)

        with open(replace_file.name, "w") as replace_file_handle:
            yaml.dump(contents, replace_file_handle)
