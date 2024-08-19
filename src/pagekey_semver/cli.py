"""Module for CLI."""

import argparse
import os
import sys
from pathlib import Path

from pagekey_semver.changelog_writer import ChangelogWriter
from pagekey_semver.git.manager import GitManager
from pagekey_semver.integrations.release_creator import (
    GitHubReleaseCreator,
    GitLabReleaseCreator,
)
from pagekey_semver.release import SemverRelease
from pagekey_semver.models import Tag
from pagekey_semver.config import load_config


def cli_entrypoint(args=sys.argv[1:]):
    """Runs pagekey-semver when called from the command-line.

    Args:
        args: List of command-line args passed by user, or fake args for testing purposes.
    """
    parser = argparse.ArgumentParser(description="PageKey Semver")
    subparsers = parser.add_subparsers(title="Commands", dest="command")
    subparsers.add_parser(
        "plan", help="Compute which version would be created. (Dry-run)"
    )
    subparsers.add_parser("apply", help="Compute version, then commit, tag, and push.")
    parsed_args = parser.parse_args(args)

    if parsed_args.command == "plan":
        dry_run = True
    elif parsed_args.command == "apply":
        dry_run = False
    else:
        parser.print_usage()
        return

    config = load_config(Path(".semver"))

    # Init classes.
    manager = GitManager(config)
    release = SemverRelease(config)
    writer = ChangelogWriter.from_config(config)

    # Check out branch on GitLab
    gitlab_branch = os.getenv("CI_COMMIT_BRANCH", "")
    if len(gitlab_branch) > 0:
        print(f"Checking out CI_COMMIT_BRANCH={gitlab_branch}")
        # Yeah, yeah, bad form to use a private var this way. Too bad.
        manager._effector.checkout(gitlab_branch)
        manager._effector.pull_all()

    # Compute tags, commits
    tags = manager.get_git_tags()
    max_tag: Tag = release.get_biggest_tag(tags)
    hash = None
    if max_tag is not None:
        hash = max_tag.name
    commits = manager.get_commit_messages_since(hash)
    release_type = release.compute_release_type(commits)
    next_version: Tag = release.compute_next_version(release_type, tags)

    print("Next version:", next_version, flush=True)
    if max_tag == next_version:
        print("No new release (nothing to do).")
        if "GITHUB_OUTPUT" in os.environ:
            with open(os.environ["GITHUB_OUTPUT"], "w") as f:
                f.write("semver_release_occurred=false")
    else:
        # Apply tag if appropriate.
        if not dry_run:
            print(f"Applying version {next_version.name}.")
            # Write to changelog.
            writer.update_changelog(next_version, commits)
            # Replace files
            print("Running file replacers.")
            for file_replacer in config.file_replacers:
                print(f"  {file_replacer.name}")
                file_replacer.perform_replace(next_version)
            # Apply tag, commit, push
            manager.apply_tag(tags, next_version)
            # Set an env var for subsequent steps in GitHub Actions.
            if "GITHUB_OUTPUT" in os.environ:
                with open(os.environ["GITHUB_OUTPUT"], "w") as f:
                    f.write("semver_release_occurred=true")
            # Create releases if enabled.
            if config.integrations.github.create_release is not None:
                GitHubReleaseCreator().create_release(
                    config.integrations.github.create_release, next_version
                )
            if config.integrations.gitlab.create_release is not None:
                GitLabReleaseCreator().create_release(
                    config.integrations.github.create_release, next_version
                )
        else:
            print(f"Would apply version {next_version.name}.", flush=True)
            print("Dry run mode - not applying version.", flush=True)
            if "GITHUB_OUTPUT" in os.environ:
                with open(os.environ["GITHUB_OUTPUT"], "w") as f:
                    f.write("semver_release_occurred=false")


if __name__ == "__main__":
    cli_entrypoint()
