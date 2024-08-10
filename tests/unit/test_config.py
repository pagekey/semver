"""Test config module."""

from unittest.mock import MagicMock, mock_open, patch

import yaml

from pagekey_semver.config import DEFAULT_CONFIG, load_config
from pagekey_semver.models import Prefix
from pagekey_semver.replace_file.json import JsonReplaceFile
from pagekey_semver.replace_file.sed import SedReplaceFile
from pagekey_semver.replace_file.toml import TomlReplaceFile
from pagekey_semver.replace_file.yaml import YamlReplaceFile

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

    @patch("builtins.open", new_callable=mock_open)
    @patch(f"{MODULE_UNDER_TEST}.os")
    def test_with_config_file_returns_merged_config(self, mock_os, mock_builtin_open):
        # Arrange.
        mock_os.environ = {}
        config_path = MagicMock()
        config_path.is_file.return_value = True
        mock_builtin_open.return_value.read.return_value = yaml.safe_dump(
            {
                "prefixes": [
                    {
                        "label": "fix",
                        "type": "patch",
                    }
                ]
            }
        )

        # Act.
        config = load_config(config_path)

        # Assert.
        assert config.prefixes[0] == Prefix(label="fix", type="patch")

    @patch(f"{MODULE_UNDER_TEST}.os")
    def test_with_env_vars_returns_overridden_config(self, mock_os):
        # Arrange.
        mock_os.environ = {
            "SEMVER_prefixes__fix": "patch",
        }
        config_path = MagicMock()
        config_path.is_file.return_value = False

        # Act.
        config = load_config(config_path)

        # Assert.
        assert config.prefixes[0] == Prefix(label="fix", type="patch")

    @patch("builtins.open", new_callable=mock_open)
    def test_with_git_user_override_parses_config(self, mock_builtin_open):
        # Arrange.
        mock_path = MagicMock()
        mock_path.is_file.return_value = True
        mock_file = mock_builtin_open.return_value
        mock_file.read.return_value = yaml.safe_dump(
            {
                "git": {
                    "name": "Steve",
                    "email": "steve@pagekey.io",
                },
            }
        )

        # Act.
        config = load_config(mock_path)

        # Assert.
        assert config.git.name == "Steve"
        assert config.git.email == "steve@pagekey.io"

    @patch("builtins.open", new_callable=mock_open)
    def test_with_tag_format_parses_config(self, mock_builtin_open):
        # Arrange.
        mock_path = MagicMock()
        mock_path.is_file.return_value = True
        mock_file = mock_builtin_open.return_value
        mock_file.read.return_value = yaml.safe_dump(
            {
                "format": "ver_%M-%m-%p",
            }
        )

        # Act.
        config = load_config(mock_path)

        # Assert.
        assert config.format == "ver_%M-%m-%p"

    @patch("builtins.open", new_callable=mock_open)
    def test_with_changelog_path_parses_config(self, mock_builtin_open):
        # Arrange.
        mock_path = MagicMock()
        mock_path.is_file.return_value = True
        mock_file = mock_builtin_open.return_value
        mock_file.read.return_value = yaml.safe_dump(
            {
                "changelog_path": "docs/CHANGELOG.md",
            }
        )

        # Act.
        config = load_config(mock_path)

        # Assert.
        assert config.changelog_path == "docs/CHANGELOG.md"

    @patch("builtins.open", new_callable=mock_open)
    def test_with_changelog_writer_parses_config(self, mock_builtin_open):
        # Arrange.
        mock_path = MagicMock()
        mock_path.is_file.return_value = True
        mock_file = mock_builtin_open.return_value
        mock_file.read.return_value = yaml.safe_dump(
            {
                "changelog_writer": "my_package:MyWriter",
            }
        )

        # Act.
        config = load_config(mock_path)

        # Assert.
        assert config.changelog_writer == "my_package:MyWriter"

    @patch("builtins.open", new_callable=mock_open)
    def test_with_replace_files_parses_config(self, mock_builtin_open):
        # Arrange.
        mock_path = MagicMock()
        mock_path.is_file.return_value = True
        mock_file = mock_builtin_open.return_value
        mock_file.read.return_value = yaml.safe_dump(
            {
                "replace_files": [
                    {
                        "name": "myfile.json",
                        "type": "json",
                        "key": "version",
                        "format": "%M.%m.%p",
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
                        "format": "%M.%m.%p",
                    },
                    {
                        "name": "myfile.yaml",
                        "type": "yaml",
                        "key": "version",
                        "format": "%M.%m.%p",
                    },
                ],
            }
        )

        # Act.
        config = load_config(mock_path)

        # Assert.
        assert config.replace_files[0] == JsonReplaceFile(
            name="myfile.json", key="version", format="%M.%m.%p"
        )
        assert config.replace_files[1] == SedReplaceFile(
            name="myfile.md", script="s/some/pattern/g"
        )
        assert config.replace_files[2] == TomlReplaceFile(
            name="myfile.toml", key="version", format="%M.%m.%p"
        )
        assert config.replace_files[3] == YamlReplaceFile(
            name="myfile.yaml", key="version", format="%M.%m.%p"
        )
