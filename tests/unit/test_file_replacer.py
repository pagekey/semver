from unittest.mock import MagicMock, call
from pagekey_semver.config import DEFAULT_CONFIG, DEFAULT_CONFIG_DICT, JsonReplaceFile, SedReplaceFile, SemverConfig, TomlReplaceFile, YamlReplaceFile
from pagekey_semver.file_replacer import FileReplacer


class TestFileReplacer:
    
    class Test_replace_all:
        
        def test_with_files_in_config_calls_replace_file(self):
            # Arrange.
            config = SemverConfig(**{**DEFAULT_CONFIG_DICT, "replace_files": [
                { "type": "json", "name": "file.json" },
                { "type": "sed", "name": "file.md", "pattern": "some_pattern" },
                { "type": "toml", "name": "file.toml" },
                { "type": "yaml", "name": "file.yaml" },
            ]})
            replacer = FileReplacer(config)
            replacer.replace_one = MagicMock()
            # Act.
            replacer.replace_all()
            # Assert.
            replacer.replace_one.assert_has_calls([
                call(JsonReplaceFile(name="file.json")),
                call(SedReplaceFile(name="file.md", pattern="some_pattern")),
                call(TomlReplaceFile(name="file.toml")),
                call(YamlReplaceFile(name="file.yaml")),
            ])

    class Test_replace_file:
        pass

    class Test_replace_json:
        pass

    class Test_replace_sed:
        pass

    class Test_replace_toml:
        pass

    class Test_replace_yaml:
        pass
