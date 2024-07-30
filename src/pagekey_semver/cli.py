from pathlib import Path
import sys

from pagekey_semver.changelog import ChangelogWriter
from pagekey_semver.config import load_config
from pagekey_semver.git import apply_tag, get_commit_messages_since, get_git_tags
from pagekey_semver.release import SemverRelease


def cli_entrypoint(args=sys.argv[1:]):
    dry_run = "--dry-run" in args
    config = load_config(Path(".semver"))
    tags = get_git_tags()
    release = SemverRelease()
    max_tag = release.get_biggest_tag(tags)
    commits = get_commit_messages_since(max_tag)
    release_type = release.compute_release_type(commits, config)
    next_version = release.compute_next_version(release_type, tags)
    ChangelogWriter().update_changelog(next_version, commits)
    print("Next version:", next_version, flush=True)
    if not dry_run:
        apply_tag(tags, next_version, config=config)
    else:
        print("Dry run mode - not applying version.", flush=True)


if __name__ == "__main__":
    cli_entrypoint()
