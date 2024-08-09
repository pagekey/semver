"""."""

from unittest.mock import MagicMock, call, mock_open, patch

import pytest
from pagekey_semver.config import DEFAULT_CONFIG, DEFAULT_CONFIG_DICT
from pagekey_semver.models import (
    JsonReplaceFile,
    SedReplaceFile,
    SemverConfig,
    TomlReplaceFile,
    YamlReplaceFile,
)
from pagekey_semver.file_replacer import FileReplacer
from pagekey_semver.release import Tag


MODULE_UNDER_TEST = "pagekey_semver.file_replacer"


class TestFileReplacer:
    class Test_replace_all:
        def test_with_files_in_config_calls_replace_file(self):
            # Arrange.
            config = SemverConfig(
                **{
                    **DEFAULT_CONFIG_DICT,
                    "replace_files": [
                        {"type": "json", "name": "file.json", "key": "version"},
                        {
                            "type": "sed",
                            "name": "file.md",
                            "script": "s/some/pattern/g",
                        },
                        {"type": "toml", "name": "file.toml", "key": "version"},
                        {"type": "yaml", "name": "file.yaml", "key": "version"},
                    ],
                }
            )
            new_version = Tag("v2.0.0", 2, 0, 0)
            replacer = FileReplacer(config, new_version)
            replacer.replace_one = MagicMock()
            # Act.
            replacer.replace_all()
            # Assert.
            replacer.replace_one.assert_has_calls(
                [
                    call(JsonReplaceFile(name="file.json", key="version")),
                    call(SedReplaceFile(name="file.md", script="s/some/pattern/g")),
                    call(TomlReplaceFile(name="file.toml", key="version")),
                    call(YamlReplaceFile(name="file.yaml", key="version")),
                ]
            )

    class Test_replace_file:
        @pytest.mark.parametrize(
            "replace_file, replace_function",
            [
                (JsonReplaceFile(name="file.json", key="version"), "replace_json"),
                (
                    SedReplaceFile(name="file.md", script="s/some/pattern/g"),
                    "replace_sed",
                ),
                (TomlReplaceFile(name="file.toml", key="version"), "replace_toml"),
                (YamlReplaceFile(name="file.yaml", key="version"), "replace_yaml"),
            ],
        )
        def test_with_file_calls_specific_type_function(
            self, replace_file, replace_function
        ):
            # Arrange.
            config = DEFAULT_CONFIG
            new_version = Tag("v2.0.0", 2, 0, 0)
            replacer = FileReplacer(config, new_version)
            setattr(replacer, replace_function, MagicMock())

            # Act.
            replacer.replace_one(replace_file)

            # Assert.
            getattr(replacer, replace_function).assert_called_with(replace_file)

    class Test_replace_json:
        @patch(f"{MODULE_UNDER_TEST}.json")
        @patch("builtins.open", new_callable=mock_open)
        def test_with_top_level_key_replaces(self, mock_builtin_open, mock_json):
            # Arrange.
            config = DEFAULT_CONFIG
            new_version = Tag("v2.0.0", 2, 0, 0)
            replacer = FileReplacer(config, new_version)
            replace_file = JsonReplaceFile(name="file.json", key="version")
            mock_json.load.return_value = {
                "version": "something",
                "other_key": "untouched",
            }

            # Act.
            replacer.replace_json(replace_file)

            # Assert.
            mock_builtin_open.assert_called_with("file.json", "w")
            # Assert first arg of first call is this:
            assert mock_json.dump.call_args_list[0][0][0] == {
                "version": "v2.0.0",
                "other_key": "untouched",
            }

        @patch(f"{MODULE_UNDER_TEST}.json")
        @patch("builtins.open", new_callable=mock_open)
        def test_with_nested_key_replaces(self, mock_builtin_open, mock_json):
            # Arrange.
            config = DEFAULT_CONFIG
            new_version = Tag("v2.0.0", 2, 0, 0)
            replacer = FileReplacer(config, new_version)
            replace_file = JsonReplaceFile(
                name="file.json", key="project.metadata.version"
            )
            mock_json.load.return_value = {
                "project": {
                    "metadata": {
                        "version": "something",
                    },
                },
                "other_key": "untouched",
            }

            # Act.
            replacer.replace_json(replace_file)

            # Assert.
            mock_builtin_open.assert_called_with("file.json", "w")
            # Assert first arg of first call is this:
            assert mock_json.dump.call_args_list[0][0][0] == {
                "project": {
                    "metadata": {
                        "version": "v2.0.0",
                    },
                },
                "other_key": "untouched",
            }

    class Test_replace_sed:
        @patch(f"{MODULE_UNDER_TEST}.shutil")
        def test_with_sed_not_installed_raises_error(self, mock_shutil):
            # Arrange.
            config = DEFAULT_CONFIG
            new_version = Tag("v2.0.0", 2, 0, 0)
            replacer = FileReplacer(config, new_version)
            replace_file = SedReplaceFile(name="file.md", script="s/something/other/g")
            mock_shutil.which.return_value = None

            # Act, Assert.
            with pytest.raises(EnvironmentError):
                replacer.replace_sed(replace_file)

        @pytest.mark.parametrize(
            "input_script, new_version, expected_command",
            [
                (
                    "s/something/else/g",
                    Tag("v2.0.0", 2, 0, 0),
                    "sed -i 's/something/else/g' file.md",
                ),
                (
                    's/^version=".*"/version=%M.%m.%p/g',
                    Tag("v2.0.0", 2, 0, 1),
                    "sed -i 's/^version=\".*\"/version=2.0.1/g' file.md",
                ),
                (
                    "s/^version='.*'/version=%M.%m.%p/g",
                    Tag("v2.0.0", 2, 0, 1),
                    "sed -i 's/^version=\\'.*\\'/version=2.0.1/g' file.md",
                ),
            ],
        )
        @patch(f"{MODULE_UNDER_TEST}.os")
        def test_with_script_calls_sed(
            self, mock_os, input_script, new_version, expected_command
        ):
            # Arrange.
            config = DEFAULT_CONFIG
            replacer = FileReplacer(config, new_version)
            replace_file = SedReplaceFile(name="file.md", script=input_script)
            mock_os.system.return_value = 0

            # Act.
            replacer.replace_sed(replace_file)

            # Assert.
            mock_os.system.assert_called_with(expected_command)

        @patch(f"{MODULE_UNDER_TEST}.os")
        def test_with_failed_sed_raises_error(self, mock_os):
            # Arrange.
            new_version = Tag("v2.0.0", 2, 0, 0)
            config = DEFAULT_CONFIG
            replacer = FileReplacer(config, new_version)
            replace_file = SedReplaceFile(
                name="some_file.md", script="some_invalid_script"
            )
            mock_os.system.return_value = -1

            # Act, Assert.
            with pytest.raises(OSError):
                replacer.replace_sed(replace_file)

    class Test_replace_toml:
        @patch(f"{MODULE_UNDER_TEST}.toml")
        @patch("builtins.open", new_callable=mock_open)
        def test_with_top_level_key_replaces(self, mock_builtin_open, mock_toml):
            # Arrange.
            config = DEFAULT_CONFIG
            new_version = Tag("v2.0.0", 2, 0, 0)
            replacer = FileReplacer(config, new_version)
            replace_file = TomlReplaceFile(name="file.toml", key="version")
            mock_toml.load.return_value = {
                "version": "something",
                "other_key": "untouched",
            }

            # Act.
            replacer.replace_toml(replace_file)

            # Assert.
            mock_builtin_open.assert_called_with("file.toml", "w")
            # Assert first arg of first call is this:
            assert mock_toml.dump.call_args_list[0][0][0] == {
                "version": "v2.0.0",
                "other_key": "untouched",
            }

        @patch(f"{MODULE_UNDER_TEST}.toml")
        @patch("builtins.open", new_callable=mock_open)
        def test_with_nested_key_replaces(self, mock_builtin_open, mock_toml):
            # Arrange.
            config = DEFAULT_CONFIG
            new_version = Tag("v2.0.0", 2, 0, 0)
            replacer = FileReplacer(config, new_version)
            replace_file = TomlReplaceFile(
                name="file.toml", key="project.metadata.version"
            )
            mock_toml.load.return_value = {
                "project": {
                    "metadata": {
                        "version": "something",
                    },
                },
                "other_key": "untouched",
            }

            # Act.
            replacer.replace_toml(replace_file)

            # Assert.
            mock_builtin_open.assert_called_with("file.toml", "w")
            # Assert first arg of first call is this:
            assert mock_toml.dump.call_args_list[0][0][0] == {
                "project": {
                    "metadata": {
                        "version": "v2.0.0",
                    },
                },
                "other_key": "untouched",
            }

    class Test_replace_yaml:
        @patch(f"{MODULE_UNDER_TEST}.yaml")
        @patch("builtins.open", new_callable=mock_open)
        def test_with_top_level_key_replaces(self, mock_builtin_open, mock_yaml):
            # Arrange.
            config = DEFAULT_CONFIG
            new_version = Tag("v2.0.0", 2, 0, 0)
            replacer = FileReplacer(config, new_version)
            replace_file = YamlReplaceFile(name="file.yaml", key="version")
            mock_yaml.safe_load.return_value = {
                "version": "something",
                "other_key": "untouched",
            }

            # Act.
            replacer.replace_yaml(replace_file)

            # Assert.
            mock_builtin_open.assert_called_with("file.yaml", "w")
            # Assert first arg of first call is this:
            assert mock_yaml.dump.call_args_list[0][0][0] == {
                "version": "v2.0.0",
                "other_key": "untouched",
            }

        @patch(f"{MODULE_UNDER_TEST}.yaml")
        @patch("builtins.open", new_callable=mock_open)
        def test_with_nested_key_replaces(self, mock_builtin_open, mock_yaml):
            # Arrange.
            config = DEFAULT_CONFIG
            new_version = Tag("v2.0.0", 2, 0, 0)
            replacer = FileReplacer(config, new_version)
            replace_file = YamlReplaceFile(
                name="file.yaml", key="project.metadata.version"
            )
            mock_yaml.safe_load.return_value = {
                "project": {
                    "metadata": {
                        "version": "something",
                    },
                },
                "other_key": "untouched",
            }

            # Act.
            replacer.replace_yaml(replace_file)

            # Assert.
            mock_builtin_open.assert_called_with("file.yaml", "w")
            # Assert first arg of first call is this:
            assert mock_yaml.dump.call_args_list[0][0][0] == {
                "project": {
                    "metadata": {
                        "version": "v2.0.0",
                    },
                },
                "other_key": "untouched",
            }
