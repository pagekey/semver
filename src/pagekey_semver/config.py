"""Module related to config files."""

import os
from pathlib import Path
from typing import List, Union

from pydantic import BaseModel, Field
import yaml

from pagekey_semver.integrations.release_creator import (
    GitHubIntegrationConfig,
    GitLabIntegrationConfig,
)
from pagekey_semver.models import (
    GitConfig,
    Prefix,
)
from pagekey_semver.file_replacer.json import JsonFileReplacer
from pagekey_semver.file_replacer.sed import SedFileReplacer
from pagekey_semver.file_replacer.toml import TomlFileReplacer
from pagekey_semver.file_replacer.yaml import YamlFileReplacer
from pagekey_semver.util.env_to_dict import convert_env_to_dict
from pagekey_semver.util.update_dict import merge_dicts


class IntegrationsConfig(BaseModel):
    """Holds all configs for integrating with external services."""

    github: GitHubIntegrationConfig = GitHubIntegrationConfig()
    gitlab: GitLabIntegrationConfig = GitLabIntegrationConfig()


FileReplacersUnion = Union[
    JsonFileReplacer, SedFileReplacer, TomlFileReplacer, YamlFileReplacer
]


class SemverConfig(BaseModel):
    """Represents config options for entire application."""

    changelog_path: str
    changelog_writer: str
    format: str
    git: GitConfig
    prefixes: List[Prefix]
    file_replacers: List[FileReplacersUnion] = Field(discriminator="type")
    integrations: IntegrationsConfig = IntegrationsConfig()


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
    file_replacers=[],
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
