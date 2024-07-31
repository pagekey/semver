import json
import os
import subprocess

import yaml

from pagekey_semver.cli import cli_entrypoint
from pagekey_semver.config import GitConfig, Prefix, SemverConfig


def test_add_tag_with_existing_project_works(tmp_path):
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

    # Set up custom config file.
    config = SemverConfig(
        format="ver_%M-%m-%p",
        git=GitConfig(
            name="my name",
            email="my@email.com"
        ),
        prefixes=[
            Prefix(label="custom", type="major"),
        ],
    )
    with open('.semver', 'w') as semver_file:
        semver_file.write(yaml.safe_dump(config.model_dump()))
    os.system("git add .semver")
    os.system("git commit -m 'custom: Add .semver'")
    
    # Act.
    # Invoke semver.
    cli_entrypoint()

    # Assert.
    assert os.path.exists("CHANGELOG.md")
    with open("CHANGELOG.md", "r") as changelog_file:
        changelog = changelog_file.read()
    assert "## v0.1.0" in changelog
    assert "fix: Add package.json" in changelog
    assert "## ver_0-1-0" in changelog
    assert "custom: Add .semver" in changelog

    result = subprocess.run(
        ["git", "tag"],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    assert result.stdout.strip() == "v0.1.0\nver_0-1-0"
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
