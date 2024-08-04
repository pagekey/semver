
import json
import os
import shutil
import toml
import yaml
from pagekey_semver.config import JsonReplaceFile, ReplaceFileType, ReplaceFileUnion, SedReplaceFile, SemverConfig, TomlReplaceFile, YamlReplaceFile
from pagekey_semver.release import Tag
from pagekey_semver.util.update_dict import set_dict_value


class FileReplacer:
    def __init__(self, config: SemverConfig, new_version: Tag):
        self._config = config
        self._new_version = new_version
    
    def replace_all(self):
        for replace_file in self._config.replace_files:
            self.replace_one(replace_file)

    def replace_one(self, file: ReplaceFileUnion):
        if file.type == ReplaceFileType.JSON:
            self.replace_json(file)
        elif file.type == ReplaceFileType.SED:
            self.replace_sed(file)
        elif file.type == ReplaceFileType.TOML:
            self.replace_toml(file)
        else:
            self.replace_yaml(file)

    def replace_json(self, replace_file: JsonReplaceFile):
        with open(replace_file.name, "r") as replace_file_handle:
            contents = json.load(replace_file_handle)
        
        set_dict_value(contents, replace_file.key, self._new_version.name)

        with open(replace_file.name, "w") as replace_file_handle:
            json.dump(contents, replace_file_handle)

    def replace_sed(self, replace_file: SedReplaceFile):
        if shutil.which("sed") is None:
            raise EnvironmentError("Sed executable not found on system - have you installed sed?")
        script_escaped = replace_file.script.replace("'", "\\'")
        script_replaced = script_escaped \
                .replace("%M", str(self._new_version.major)) \
                .replace("%m", str(self._new_version.minor)) \
                .replace("%p", str(self._new_version.patch))
        os.system(f"sed -i '{script_replaced}' {replace_file.name}")

    def replace_toml(self, replace_file: TomlReplaceFile):
        with open(replace_file.name, "r") as replace_file_handle:
            contents = toml.load(replace_file_handle)
        
        set_dict_value(contents, replace_file.key, self._new_version.name)

        with open(replace_file.name, "w") as replace_file_handle:
            toml.dump(contents, replace_file_handle)

    def replace_yaml(self, replace_file: YamlReplaceFile):
        with open(replace_file.name, "r") as replace_file_handle:
            contents = yaml.load(replace_file_handle)
        
        set_dict_value(contents, replace_file.key, self._new_version.name)

        with open(replace_file.name, "w") as replace_file_handle:
            yaml.dump(contents, replace_file_handle)
