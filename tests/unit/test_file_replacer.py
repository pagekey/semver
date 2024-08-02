import json
from unittest.mock import MagicMock, call, mock_open, patch

import pytest
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

        @pytest.mark.parametrize("replace_file, replace_function", [
            (JsonReplaceFile(name="file.json"), "replace_json"),
            (SedReplaceFile(name="file.md", pattern="some_pattern"), "replace_sed"),
            (TomlReplaceFile(name="file.toml"), "replace_toml"),
            (YamlReplaceFile(name="file.yaml"), "replace_yaml")
        ])
        def test_with_file_calls_specific_type_function(self, replace_file, replace_function):
            # Arrange.
            config = DEFAULT_CONFIG
            replacer = FileReplacer(config)
            setattr(replacer, replace_function, MagicMock())

            # Act.
            replacer.replace_one(replace_file)

            # Assert.
            getattr(replacer, replace_function).assert_called_with(replace_file)
        

    class Test_replace_json:
        
        @patch('builtins.open', new_callable=mock_open)
        def test_with_top_level_key_replaces(self, mock_builtin_open):
            # Arrange.
            config = DEFAULT_CONFIG
            replacer = FileReplacer(config)
            replace_file = JsonReplaceFile(name="file.json", key="version")
            mock_file_handle = mock_builtin_open.return_value
            mock_file_handle.read.return_value = json.dumps({
                "version": "something",
            })

            # Act.
            replacer.replace_json(replace_file)

            # Assert.
            mock_builtin_open.assert_called_with("file.json", "r")
            # TODO: more assertions, pass new_version, update JsonReplaceFile model to have key


        @patch('builtins.open', new_callable=mock_open)
        def test_with_nested_key_replaces(self, mock_builtin_open):
            # Arrange.
            config = DEFAULT_CONFIG
            replacer = FileReplacer(config)
            replace_file = JsonReplaceFile(name="file.json")

            # Act.
            replacer.replace_json(replace_file)

            # Assert.
            pass


    class Test_replace_sed:
        pass


    class Test_replace_toml:
        pass


    class Test_replace_yaml:
        pass
