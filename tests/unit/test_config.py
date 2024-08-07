"""Test config module."""


from unittest.mock import MagicMock, mock_open, patch

import yaml

from pagekey_semver.config import DEFAULT_CONFIG, DEFAULT_CONFIG_DICT, JsonReplaceFile, Prefix, SedReplaceFile, SemverConfig, TomlReplaceFile, ReplaceFileType, YamlReplaceFile, load_config

MODULE_UNDER_TEST = "pagekey_semver.config"


class Test_load_config:

    @patch(f"{MODULE_UNDER_TEST}.os")
    def test_with_no_config_file_returns_default_config(self, mock_os):
        # Arrange.
        mock_os.environ = {}
        config_path = MagicMock()
        config_path.is_file.return_value = False

        # Act.
        config = load_config(config_path)

        # Assert.
        assert config == DEFAULT_CONFIG


    @patch('builtins.open', new_callable=mock_open)
    @patch(f"{MODULE_UNDER_TEST}.os")
    def test_with_config_file_returns_merged_config(self, mock_os, mock_builtin_open):
        # Arrange.
        mock_os.environ = {}
        config_path = MagicMock()
        config_path.is_file.return_value = True
        mock_builtin_open.return_value.read.return_value = yaml.safe_dump({
            "prefixes": [
                {
                    "label": "fix",
                    "type": "patch",
                }
            ]
        })

        # Act.
        config = load_config(config_path)

        # Assert.
        assert config.prefixes[0] == Prefix(label="fix", type="patch")


    @patch(f"{MODULE_UNDER_TEST}.os")
    def test_with_env_vars_returns_overridden_config(self, mock_os):
        # Arrange.
        mock_os.environ = {
            "SEMVER_prefixes__0__label": "fix",
            "SEMVER_prefixes__0__type": "patch",
        }
        config_path = MagicMock()
        config_path.is_file.return_value = False

        # Act.
        config = load_config(config_path)

        # Assert.
        assert config.prefixes[0] == Prefix(label="fix", type="patch")


    # @patch(f"{MODULE_UNDER_TEST}.SemverConfig")
    # @patch('builtins.open', new_callable=mock_open)
    # def test_with_file_not_found_returns_default_config(self, mock_builtin_open, mock_variable_parser_cls, mock_os, mock_semver_config_cls):
    #     # Arrange.
    #     mock_path = MagicMock()
    #     mock_path.is_file.return_value = False
    #     mock_variable_parser = mock_variable_parser_cls.return_value

    #     # Act.
    #     config = load_config(mock_path)

    #     # Assert.
    #     mock_path.is_file.assert_called()
    #     mock_builtin_open.assert_not_called()
    #     mock_variable_parser_cls.assert_called_with(mock_os.environ)
    #     mock_variable_parser.merge_config.assert_called_with(DEFAULT_CONFIG_DICT)
    #     mock_semver_config_cls.assert_called_with(DEFAULT_CONFIG_DICT)



    # @patch(f"{MODULE_UNDER_TEST}.SemverConfig")
    # @patch(f"{MODULE_UNDER_TEST}.os")
    # @patch(f'{MODULE_UNDER_TEST}.VariableParser')
    # @patch('builtins.open', new_callable=mock_open)
    # def test_with_existing_file_parses_and_merges_configs(self, mock_builtin_open, mock_variable_parser_cls, mock_os, mock_semver_config_cls):
    #     # Arrange.
    #     mock_path = MagicMock()
    #     mock_path.is_file.return_value = True
    #     mock_file = mock_builtin_open.return_value
    #     config_dict = {
    #         "prefixes": [
    #             {
    #                 "label": "fix",
    #                 "type": "patch",
    #             }
    #         ]
    #     }
    #     mock_file.read.return_value = yaml.safe_dump(config_dict)
    #     mock_variable_parser = mock_variable_parser_cls.return_value

    #     # Act.
    #     config = load_config(mock_path)

    #     # Assert.
    #     mock_path.is_file.assert_called()
    #     mock_builtin_open.assert_called_with(mock_path, "r")
    #     mock_file.read.assert_called()
    #     mock_variable_parser_cls.assert_called_with(mock_os.environ)
    #     mock_variable_parser.merge_config.assert_called_with({**DEFAULT_CONFIG_DICT, **config_dict})
    #     mock_semver_config_cls.assert_called_with({**DEFAULT_CONFIG_DICT, **config_dict})


    @patch('builtins.open', new_callable=mock_open)
    def test_with_git_user_override_parses_config(self, mock_builtin_open):
        # Arrange.
        mock_path = MagicMock()
        mock_path.is_file.return_value = True
        mock_file = mock_builtin_open.return_value
        mock_file.read.return_value = yaml.safe_dump({
            "git": {
                "name": "Steve",
                "email": "steve@pagekey.io",
            },
        })

        # Act.
        config = load_config(mock_path)

        # Assert.
        assert config.git.name == "Steve"
        assert config.git.email == "steve@pagekey.io"


    @patch('builtins.open', new_callable=mock_open)
    def test_with_tag_format_parses_config(self, mock_builtin_open):
        # Arrange.
        mock_path = MagicMock()
        mock_path.is_file.return_value = True
        mock_file = mock_builtin_open.return_value
        mock_file.read.return_value = yaml.safe_dump({
            "format": "ver_%M-%m-%p",
        })

        # Act.
        config = load_config(mock_path)

        # Assert.
        assert config.format == "ver_%M-%m-%p"


    @patch('builtins.open', new_callable=mock_open)
    def test_with_changelog_path_parses_config(self, mock_builtin_open):
        # Arrange.
        mock_path = MagicMock()
        mock_path.is_file.return_value = True
        mock_file = mock_builtin_open.return_value
        mock_file.read.return_value = yaml.safe_dump({
            "changelog_path": "docs/CHANGELOG.md",
        })

        # Act.
        config = load_config(mock_path)

        # Assert.
        assert config.changelog_path == "docs/CHANGELOG.md"


    @patch('builtins.open', new_callable=mock_open)
    def test_with_changelog_writer_parses_config(self, mock_builtin_open):
        # Arrange.
        mock_path = MagicMock()
        mock_path.is_file.return_value = True
        mock_file = mock_builtin_open.return_value
        mock_file.read.return_value = yaml.safe_dump({
            "changelog_writer": "my_package:MyWriter",
        })

        # Act.
        config = load_config(mock_path)

        # Assert.
        assert config.changelog_writer == "my_package:MyWriter"


    @patch('builtins.open', new_callable=mock_open)
    def test_with_replace_files_parses_config(self, mock_builtin_open):
        # Arrange.
        mock_path = MagicMock()
        mock_path.is_file.return_value = True
        mock_file = mock_builtin_open.return_value
        mock_file.read.return_value = yaml.safe_dump({
            "replace_files": [
                {
                    "name": "myfile.json",
                    "type": "json",
                    "key": "version",
                },
                {
                    "name": "myfile.md",
                    "type": "sed",
                    "script": "s/some/pattern/g",
                },
                {
                    "name": "myfile.toml",
                    "type": "toml",
                    "key": "version",
                },
                {
                    "name": "myfile.yaml",
                    "type": "yaml",
                    "key": "version",
                },
            ],
        })

        # Act.
        config = load_config(mock_path)

        # Assert.
        assert config.replace_files[0] == JsonReplaceFile(name="myfile.json", key="version")
        assert config.replace_files[1] == SedReplaceFile(name="myfile.md", script="s/some/pattern/g")
        assert config.replace_files[2] == TomlReplaceFile(name="myfile.toml", key="version")
        assert config.replace_files[3] == YamlReplaceFile(name="myfile.yaml", key="version")
