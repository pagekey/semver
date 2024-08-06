"""Test config module."""


from unittest.mock import MagicMock, call, mock_open, patch

import pytest
import yaml

from pagekey_semver.config import DEFAULT_CONFIG, DEFAULT_CONFIG_DICT, JsonReplaceFile, SedReplaceFile, SemverConfig, TomlReplaceFile, ReplaceFileType, YamlReplaceFile, apply_env_to_config_dict, get_all_prefixed_env_vars, load_config
from pagekey_semver.release import ReleaseType

MODULE_UNDER_TEST = "pagekey_semver.config"


class Test_load_config:
    @patch(f'{MODULE_UNDER_TEST}.apply_env_to_config_dict')
    @patch('builtins.open', new_callable=mock_open)
    def test_with_file_not_found_returns_default_config(self, mock_builtin_open, mock_apply_env):
        # Arrange.
        mock_path = MagicMock()
        mock_path.is_file.return_value = False

        # Act.
        config = load_config(mock_path)

        # Assert.
        mock_path.is_file.assert_called()
        mock_builtin_open.assert_not_called()
        assert config == mock_apply_env.return_value
        mock_apply_env.assert_called_with(DEFAULT_CONFIG_DICT)


    @patch(f'{MODULE_UNDER_TEST}.apply_env_to_config_dict')
    @patch('builtins.open', new_callable=mock_open)
    def test_with_existing_file_parses_and_merges_configs(self, mock_builtin_open, mock_apply_env):
        # Arrange.
        mock_path = MagicMock()
        mock_path.is_file.return_value = True
        mock_file = mock_builtin_open.return_value
        config_dict = {
            "prefixes": [
                {
                    "label": "fix",
                    "type": "patch",
                }
            ]
        }
        mock_file.read.return_value = yaml.safe_dump(config_dict)

        # Act.
        config = load_config(mock_path)

        # Assert.
        mock_path.is_file.assert_called()
        mock_builtin_open.assert_called_with(mock_path, "r")
        mock_file.read.assert_called()
        assert config == mock_apply_env.return_value
        mock_apply_env.assert_called_with({**DEFAULT_CONFIG_DICT, **config_dict})


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


class Test_get_all_prefixed_env_vars:
    
    @pytest.mark.parametrize("environ, expected", [
        (
            {
                "PATH": "something",
                "TEST_VAR": "something else",
            },
            {}
        ),
        (
            {
                "SEMVER_changelog_path": "CHANGELOG.md",
                "SEMVER_git__name": "me",
                "SEMVER_replace_files__0": "testing",
                "SOME_OTHER_VAR": "irrelevant"
            },
            {
                "SEMVER_changelog_path": "CHANGELOG.md",
                "SEMVER_git__name": "me",
                "SEMVER_replace_files__0": "testing",
            }
        ),
    ])
    def test_with_env_vars_returns_prefixed_vars(self, environ, expected):
        # Act.
        result = get_all_prefixed_env_vars(environ)

        # Assert.
        # assert result == expected


class Test_apply_env_to_config_dict:

    def test_with_no_env_vars_set_returns_same_dict(self):
        # Arrange.
        pass
        
        # Act.
        apply_env_to_config_dict(DEFAULT_CONFIG_DICT)
        
        # Assert.
        pass


# @patch('os.getenv')
# @patch('builtins.open', new_callable=mock_open)
# def test_load_config_with_env_vars_for_git_user_parses_config(mock_builtin_open, mock_getenv):
#     # Arrange.
#     mock_getenv.side_effect = [
#         "git_user",
#         "git@email.com",
#     ]
#     mock_path = MagicMock()
#     mock_path.is_file.return_value = True
#     mock_file = mock_builtin_open.return_value
#     mock_file.read.return_value = yaml.safe_dump({
#         "git": {
#             "name": "$GIT_USER",
#             "email": "$GIT_EMAIL",
#         },
#     })

#     # Act.
#     config = load_config(mock_path)

#     # Assert.
#     mock_getenv.assert_has_calls([
#         call("GIT_USER"),
#         call("GIT_EMAIL"),
#     ])
#     assert config.git.name == "git_user"
#     assert config.git.email == "git@email.com"
