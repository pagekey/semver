import sys

from pagekey_semver.lib import (
    apply_tag,
    compute_next_version,
    compute_release_type,
    get_biggest_tag,
    get_commit_messages_since,
    get_git_tags,
)


def cli_entrypoint(args=sys.argv[1:]):
    dry_run = "--dry-run" in args
    tags = get_git_tags()
    max_tag = get_biggest_tag(tags)
    commits = get_commit_messages_since(max_tag)
    release_type = compute_release_type(commits)
    next_version = compute_next_version(release_type, tags)
    if not dry_run:
        apply_tag(next_version)
    else:
        print("Dry run mode - not applying version.")


if __name__ == "__main__":
    cli_entrypoint()
