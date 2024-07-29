"""Test config module."""


from unittest.mock import MagicMock, call, mock_open, patch

import yaml

from pagekey_semver.config import DEFAULT_CONFIG, DEFAULT_CONFIG_DICT, SemverConfig, load_config
from pagekey_semver.release import ReleaseType

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
    mock_file.read.return_value = yaml.safe_dump({
        "prefixes": [
            {
                "label": "fix",
                "type": "patch",
            }
        ]
    })

    # Act.
    config = load_config(mock_path)

    # Assert.
    mock_path.is_file.assert_called()
    mock_builtin_open.assert_called_with(mock_path, "r")
    mock_file.read.assert_called()
    assert len(config.prefixes) == 1
    assert config.prefixes[0].label == "fix"
    assert config.prefixes[0].type == ReleaseType.PATCH


@patch('builtins.open', new_callable=mock_open)
def test_load_config_with_git_user_override_parses_config(mock_builtin_open):
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


@patch('os.getenv')
@patch('builtins.open', new_callable=mock_open)
def test_load_config_with_tag_format_parses_config(mock_builtin_open, mock_getenv):
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
