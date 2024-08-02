
from pagekey_semver.config import JsonReplaceFile, ReplaceFileType, ReplaceFileUnion, SedReplaceFile, SemverConfig, TomlReplaceFile, YamlReplaceFile


class FileReplacer:
    def __init__(self, config: SemverConfig):
        self._config = config
    
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

    def replace_json(self, file: JsonReplaceFile):
        pass

    def replace_sed(self, file: SedReplaceFile):
        pass

    def replace_toml(self, file: TomlReplaceFile):
        pass

    def replace_yaml(self, file: YamlReplaceFile):
        pass
