"""Test config module."""


from pathlib import Path
from unittest.mock import MagicMock, mock_open, patch

from pagekey_semver.config import DEFAULT_CONFIG, load_config

MODULE_UNDER_TEST = "pagekey_semver.config"


@patch(f'{MODULE_UNDER_TEST}.os')
@patch('builtins.open', new_callable=mock_open)
def test_load_config_with_file_not_found_returns_default_config(mock_builtin_open, mock_os):
    # Arrange.
    mock_path = MagicMock()
    mock_path.is_file.return_value = False

    # Act.
    config = load_config(mock_path)

    # Assert.
    mock_path.is_file.assert_called()
    mock_builtin_open.assert_not_called()
    assert config == DEFAULT_CONFIG



# def test_parse_config
    # # Arrange.
    # mock_file = mock_open.return_value

    # # Act.
    # config = load_config(".semver")

    # # Assert.
    # mock_open.assert_called_with(".semver", "r")
    
    # mock_file.write.assert_has_calls([
    #     call(f"## {version}\n\n"),
    #     call("- fix: Do something somewhat important (aaaaa2)\n"),
    #     call("- feat: Add something (aaaaa3)\n"),
    #     call("- major: Wow this is a big deal (aaaaa5)\n"),
    #     call("\n"),
    # ])
