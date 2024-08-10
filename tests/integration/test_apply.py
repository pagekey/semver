"""Integration tests.

These tests actually create git repos and run the pagekey-semver tool on the real filesystem.

The docstring for each test outlines the use case being tested.
"""

import json
import os
import subprocess
from unittest import mock

import toml
import yaml

from pagekey_semver.cli import cli_entrypoint
from pagekey_semver.config import SemverConfig
from pagekey_semver.models import GitConfig, Prefix
from pagekey_semver.file_replacer.json import JsonFileReplacer
from pagekey_semver.file_replacer.sed import SedFileReplacer
from pagekey_semver.file_replacer.toml import TomlFileReplacer
from pagekey_semver.file_replacer.yaml import YamlFileReplacer


def setup_git_repo(tmp_path):
    """Initialize a git repo given a temp path.

    Sets up remote and adds first commit.

    Helper method for the integration tests below.
    """
    # Set up Git user/email.
    os.system('git config --global user.email "integration@test.com"')
    os.system('git config --global user.name "integration tester"')
    # Create a temporary directory representing a project.
    tmp_dir = tmp_path / "project"
    tmp_dir.mkdir()
    # Set up example git project.
    os.chdir(tmp_dir)
    os.system("git init")
    os.system("touch Cargo.toml")
    os.system("git add --all")
    os.system("git commit -m 'Initial commit'")
    os.system("touch package.json")
    os.system("git add package.json")
    os.system("git commit -m 'fix: Add package.json'")
    # Set up remote.
    os.chdir(tmp_path)
    os.system("git clone project remote")
    os.chdir(tmp_path / "remote")
    os.system("git config receive.denyCurrentBranch ignore")
    os.chdir(tmp_dir)
    os.system("git remote add origin ../remote")


def test_default_config(tmp_path):
    """Test using with default options.

    Use case:

    1. User creates a git repo.
    2. User runs pagekey-semver.
    3. Pagekey-semver updates version, tag, and changelog using default config.
    """
    # Arrange.
    setup_git_repo(tmp_path)
    # Make additional commit that does not trigger release.
    os.system("touch package2.json")
    os.system("git add package2.json")
    os.system("git commit -m 'Add package2.json'")

    # Act.
    # Invoke semver.
    cli_entrypoint(["apply"])

    # Assert.
    assert os.path.exists("CHANGELOG.md")
    result = subprocess.run(
        ["git", "tag"],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    assert result.stdout.strip() == "v0.1.0"
    assert os.path.exists("CHANGELOG.md")
    with open("CHANGELOG.md", "r") as changelog_file:
        changelog = changelog_file.read()
    assert "## v0.1.0\n" in changelog
    assert "- fix: Add package.json" in changelog


def test_custom_config_and_changelog_writer(tmp_path):
    """Test using custm config and custom changelog writer.

    Use case:

    1. User creates a git repo.
    2. User writes their own ChangelogWriter class.
    3. User creates a custom `.semver` config file and references the custom changelog writer.
    4. User runs pagekey-semver.
    5. Pagekey-semver parses the config and uses the custom changelog writer.
    """
    # Arrange.
    setup_git_repo(tmp_path)
    # Create custom changelog writer.
    with open("custom_changelog_writer.py", "w") as writer_src:
        writer_src.write("""
from pagekey_semver.changelog_writer import ChangelogWriter
class CustomChangelogWriter(ChangelogWriter):
    def write_changelog(self, changelog_file, version, commits):
        changelog_file.write("Hello " + version.name + "\\n")
        for commit in commits:
            changelog_file.write("> " + commit.message + "\\n")
""")
    # Add files to be replaced
    with open("file_replacer.json", "w") as file_handle:
        json.dump(
            {
                "my": {
                    "version": "hello",
                },
                "something": "else",
            },
            file_handle,
        )
    with open("file_replacer.md", "w") as file_handle:
        file_handle.write("# Some Project\n\nThis is version 0.0.0 of the project.\n")
    with open("file_replacer.toml", "w") as file_handle:
        toml.dump(
            {
                "my_version": "hello",
                "something": "else",
            },
            file_handle,
        )
    with open("file_replacer.yaml", "w") as file_handle:
        yaml.dump(
            {
                "my_version": "hello",
                "something": "else",
            },
            file_handle,
        )
    # Set up custom config file.
    config = SemverConfig(
        changelog_path="docs/CHANGELOG.md",
        changelog_writer="custom_changelog_writer:CustomChangelogWriter",
        format="ver_%M-%m-%p",
        git=GitConfig(name="my name", email="my@email.com"),
        prefixes=[
            Prefix(label="custom", type="major"),
        ],
        file_replacers=[
            JsonFileReplacer(
                name="file_replacer.json", key="my.version", format="%M.%m.%p"
            ),
            SedFileReplacer(
                name="file_replacer.md",
                script="s/^This/This is version %M.%m.%p of the project./g",
            ),
            TomlFileReplacer(
                name="file_replacer.toml", key="my_version", format="%M.%m.%p"
            ),
            YamlFileReplacer(
                name="file_replacer.yaml", key="my_version", format="%M.%m.%p"
            ),
        ],
    )

    # Make test commit.
    with open(".semver", "w") as semver_file:
        semver_file.write(yaml.safe_dump(config.model_dump()))
    os.system("git add .semver")
    os.system("git commit -m 'custom: Add .semver'")

    # Act.
    # Invoke semver.
    cli_entrypoint(["apply"])

    # Assert.
    assert os.path.exists("docs/CHANGELOG.md")
    with open("docs/CHANGELOG.md", "r") as changelog_file:
        changelog = changelog_file.read()
    assert "Hello ver_0-1-0\n" in changelog
    assert "> custom: Add .semver\n" in changelog

    result = subprocess.run(
        ["git", "tag"],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    assert result.stdout.strip() == "ver_0-1-0"
    result = subprocess.run(
        ["git", "show", "-s", "--format=%an", "HEAD"],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    assert result.stdout.strip() == "my name"
    result = subprocess.run(
        ["git", "show", "-s", "--format=%ae", "HEAD"],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    assert result.stdout.strip() == "my@email.com"
    # Make sure file_replacer stuff worked.
    with open("file_replacer.json") as file_handle:
        the_dict = json.load(file_handle)
        assert the_dict["my"]["version"] == "0.1.0"
        assert the_dict["something"] == "else"
    with open("file_replacer.md") as file_handle:
        the_contents = file_handle.read()
        assert "This is version 0.1.0 of the project." in the_contents
    with open("file_replacer.toml") as file_handle:
        the_dict = toml.load(file_handle)
        assert the_dict["my_version"] == "0.1.0"
        assert the_dict["something"] == "else"
    with open("file_replacer.yaml") as file_handle:
        the_dict = yaml.safe_load(file_handle)
        assert the_dict["my_version"] == "0.1.0"
        assert the_dict["something"] == "else"
    # Make sure Git user has been restored.
    result = subprocess.run(
        ["git", "config", "user.email"],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    assert result.stdout.strip() == "integration@test.com"
    result = subprocess.run(
        ["git", "config", "user.name"],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    assert result.stdout.strip() == "integration tester"


def test_env_overrides(tmp_path):
    """Test using environment variable overrides.

    Use case:

    1. User creates a git repo.
    2. User sets environment variables to override file-based configs.
    3. User runs pagekey-semver.
    4. Pagekey-semver parses/uses the environment variables.
    """
    # Arrange.
    setup_git_repo(tmp_path)
    # Make sure environment overrides work.
    env_overrides = {
        # Top-level key
        "SEMVER_format": "ver_%M-%m-%p",
        # Nested key
        "SEMVER_git__name": "my name",
        # Prefix
        "SEMVER_prefixes__custom": "minor",
        # Replace File
        "SEMVER_file_replacers__0__name": "test.json",
        "SEMVER_file_replacers__0__type": "json",
        "SEMVER_file_replacers__0__key": "version",
        "SEMVER_file_replacers__0__format": "%M.%m.%p",
    }
    # Make a test commit.
    with open("test.json", "w") as file_handle:
        json.dump(
            {
                "version": "replace me",
            },
            file_handle,
        )
    os.system("git add test.json")
    os.system("git commit -m 'custom: Add test.json'")

    # Act.
    # Invoke semver.
    with mock.patch.dict(os.environ, env_overrides):
        cli_entrypoint(["apply"])

    # Assert.
    # Check CHANGELOG.
    assert os.path.exists("CHANGELOG.md")
    with open("CHANGELOG.md", "r") as changelog_file:
        changelog = changelog_file.read()
    assert "## ver_0-1-0\n" in changelog
    assert "- custom: Add test.json" in changelog
    # Check replaced JSON file.
    with open("test.json", "r") as file_handle:
        file_dict = json.load(file_handle)
    assert file_dict["version"] == "0.1.0"
