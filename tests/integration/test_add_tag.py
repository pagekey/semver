import json
import os
import subprocess
from unittest.mock import patch

import toml
import yaml

from pagekey_semver.cli import cli_entrypoint
from pagekey_semver.models import GitConfig, JsonReplaceFile, Prefix, SedReplaceFile, SemverConfig, TomlReplaceFile, YamlReplaceFile

def setup_git_repo(tmp_path):
    # Arrange.
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
    # Arrange.
    setup_git_repo(tmp_path)

    # Act.
    # Invoke semver.
    cli_entrypoint()

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

def test_custom_config(tmp_path):
    # Arrange.
    setup_git_repo(tmp_path)
    # Create custom changelog writer.
    with open("custom_changelog_writer.py", 'w') as writer_src:
        writer_src.write("""
from pagekey_semver.changelog import ChangelogWriter
class CustomChangelogWriter(ChangelogWriter):
    def write_changelog(self, changelog_file, version, commits):
        changelog_file.write("Hello " + version.name + "\\n")
        for commit in commits:
            changelog_file.write("> " + commit.message + "\\n")
""")
    # Add files to be replaced
    with open("replace_file.json", "w") as file_handle:
        json.dump({
            "my": {
                "version": "hello",
            },
            "something": "else",
        }, file_handle)
    with open("replace_file.md", "w") as file_handle:
        file_handle.write("# Some Project\n\nThis is version 0.0.0 of the project.\n")
    with open("replace_file.toml", "w") as file_handle:
        toml.dump({
            "my_version": "hello",
            "something": "else",
        }, file_handle)
    with open("replace_file.yaml", "w") as file_handle:
        yaml.dump({
            "my_version": "hello",
            "something": "else",
        }, file_handle)
    # Set up custom config file.
    config = SemverConfig(
        changelog_path="docs/CHANGELOG.md",
        changelog_writer="custom_changelog_writer:CustomChangelogWriter",
        format="overridden by env",
        git=GitConfig(
            name="overridden by env",
            email="my@email.com"
        ),
        prefixes=[
            Prefix(label="custom", type="major"),
        ],
        replace_files=[
            JsonReplaceFile(name="replace_file.json", key="my.version"),
            SedReplaceFile(name="replace_file.md", script="s/^This/This is version %M.%m.%p of the project./g"),
            TomlReplaceFile(name="replace_file.toml", key="my_version"),
            YamlReplaceFile(name="replace_file.yaml", key="my_version"),
        ],
    )
    # Make sure environment overrides work.
    # mock_environ = {}
    # # Top-level key
    # mock_environ["SEMVER_format"] = "ver_%M-%m-%p"
    # # Nested key
    # mock_environ["SEMVER_git__name"] = "my name"

    # Make test commit.
    with open('.semver', 'w') as semver_file:
        semver_file.write(yaml.safe_dump(config.model_dump()))
    os.system("git add .semver")
    os.system("git commit -m 'custom: Add .semver'")
    
    # Act.
    # Invoke semver.
    cli_entrypoint()

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
    # Make sure replace_file stuff worked.
    with open("replace_file.json") as file_handle:
        the_dict = json.load(file_handle)
        assert the_dict["my"]["version"] == "ver_0-1-0"
        assert the_dict["something"] == "else"
    with open("replace_file.md") as file_handle:
        the_contents = file_handle.read()
        assert "This is version 0.1.0 of the project." in the_contents
    with open("replace_file.toml") as file_handle:
        the_dict = toml.load(file_handle)
        assert the_dict["my_version"] == "ver_0-1-0"
        assert the_dict["something"] == "else"
    with open("replace_file.yaml") as file_handle:
        the_dict = yaml.safe_load(file_handle)
        assert the_dict["my_version"] == "ver_0-1-0"
        assert the_dict["something"] == "else"
