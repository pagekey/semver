"""Module for CLI."""

from pathlib import Path
import sys

from pagekey_semver.changelog import ChangelogWriter
from pagekey_semver.file_replacer import FileReplacer
from pagekey_semver.git import GitManager
from pagekey_semver.release import SemverRelease, Tag
from pagekey_semver.config import load_config


def cli_entrypoint(args=sys.argv[1:]):
    """Runs pagekey-semver when called from the command-line.
    
    Args:
        args: List of command-line args passed by user, or fake args for testing purposes.
    """
    dry_run = "--dry-run" in args
    config = load_config(Path(".semver"))

    # Init classes.
    manager = GitManager(config)
    release = SemverRelease(config)
    writer = ChangelogWriter.from_config(config)

    # Compute tags, commits
    tags = manager.get_git_tags()
    max_tag: Tag = release.get_biggest_tag(tags)
    hash = None
    if max_tag is not None:
        hash = max_tag.name
    commits = manager.get_commit_messages_since(hash)
    release_type = release.compute_release_type(commits)
    next_version = release.compute_next_version(release_type, tags)

    # Write to changelog.
    writer.update_changelog(next_version, commits)
    print("Next version:", next_version, flush=True)

    # Apply tag if appropriate.
    if not dry_run:
        # Replace files
        file_replacer = FileReplacer(config, next_version)
        file_replacer.replace_all()
        # Apply tag, commit, push
        manager.apply_tag(tags, next_version)
    else:
        print("Dry run mode - not applying version.", flush=True)


if __name__ == "__main__":
    cli_entrypoint()
