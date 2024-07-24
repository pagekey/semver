"""Test config module."""


from pathlib import Path
from unittest.mock import MagicMock, mock_open, patch

from pagekey_semver.config import DEFAULT_CONFIG_DICT, SemverConfig, load_config

MODULE_UNDER_TEST = "pagekey_semver.config"


@patch('builtins.open', new_callable=mock_open)
def test_load_config_with_file_not_found_returns_default_config(mock_builtin_open):
    # Arrange.
    mock_path = MagicMock()
    mock_path.is_file.return_value = False

    # Act.
    config = load_config(mock_path)

    # Assert.
    mock_path.is_file.assert_called()
    mock_builtin_open.assert_not_called()
    assert config == SemverConfig(**DEFAULT_CONFIG_DICT)


@patch('builtins.open', new_callable=mock_open)
def test_load_config_with_existing_file_parses_and_merges_configs(mock_builtin_open):
    # Arrange.
    mock_path = MagicMock()
    mock_path.is_file.return_value = True
    mock_file = mock_builtin_open.return_value
    mock_file.read.return_value = '{"prefixes": []}'

    # Act.
    config = load_config(mock_path)

    # Assert.
    mock_path.is_file.assert_called()
    mock_builtin_open.assert_called_with(mock_path, "r")
    mock_file.read.assert_called()
    assert len(config.prefixes) == 0
