
from pagekey_semver.config import ReplaceFileUnion, SemverConfig


class FileReplacer:
    def __init__(self, config: SemverConfig):
        self._config = config
    
    def replace_all(self):
        for replace_file in self._config.replace_files:
            self.replace_one(replace_file)

    def replace_one(self, file: ReplaceFileUnion):
        pass
