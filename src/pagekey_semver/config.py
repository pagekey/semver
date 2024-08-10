"""Module related to config files."""

import os
from pathlib import Path

import yaml

from pagekey_semver.models import GitConfig, Prefix, SemverConfig
from pagekey_semver.util.env_to_dict import convert_env_to_dict
from pagekey_semver.util.update_dict import merge_dicts


DEFAULT_CONFIG = SemverConfig(
    changelog_path="CHANGELOG.md",
    changelog_writer="pagekey_semver.changelog_writer:DefaultChangelogWriter",
    format="v%M.%m.%p",
    git=GitConfig(
        name="PageKey Semver",
        email="semver@pagekey.io",
    ),
    prefixes=[
        Prefix(label="major", type="major"),
        Prefix(label="minor", type="minor"),
        Prefix(label="feat", type="minor"),
        Prefix(label="fix", type="patch"),
    ],
    replace_files=[],
)
DEFAULT_CONFIG_DICT = DEFAULT_CONFIG.model_dump()


def load_config(config_path: Path) -> SemverConfig:
    """Load config from default, file, environment (in that order).

    Args:
        config_path: Path to config to parse.

    Returns:
        SemverConfig representing merged config from defaults, config file, and environment settings.
    """
    # Get the file config.
    if config_path.is_file():
        with open(config_path, "r") as file_handle:
            custom_config = yaml.safe_load(file_handle.read())
        config_without_env = merge_dicts(DEFAULT_CONFIG_DICT, custom_config)
    else:
        config_without_env = DEFAULT_CONFIG_DICT

    # Get the config defined by environment variables.
    env_config = convert_env_to_dict(os.environ)

    # Merge the file config and the environment config.
    # Environment takes precedence.
    final_config = merge_dicts(config_without_env, env_config)
    return SemverConfig(**final_config)
