#!/usr/bin/env python3
"""."""

import enum
import os
import re
import subprocess
from typing import List


class ReleaseType(enum.Enum):
    NO_RELEASE = 0
    PATCH = 1
    MINOR = 2
    MAJOR = 3


PREFIXES = {
    "fix": ReleaseType.PATCH,
    "feat": ReleaseType.MINOR,
    "major": ReleaseType.MAJOR,
}


def get_git_tags() -> List[str]:
    """."""
    try:
        result = subprocess.run(
            ["git", "tag"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        # Split the output into lines (each tag is on a new line)
        tags = result.stdout.strip().split("\n")
        return tags
    except subprocess.CalledProcessError as e:
        print(f"Error getting git tags: {e.stderr}")
        return []


def get_commit_messages_since(commit_hash) -> List[str]:
    """."""
    try:
        result = subprocess.run(
            ["git", "log", f"{commit_hash}..HEAD", "--pretty=format:%s"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        # Split the output into lines (each line is a commit message)
        commit_messages = result.stdout.strip().split("\n")
        return commit_messages
    except subprocess.CalledProcessError as e:
        print(f"Error getting commit messages: {e.stderr}")
        return []


def compute_release_type(commits: List[str]) -> ReleaseType:
    """."""
    release_type = ReleaseType.NO_RELEASE
    for commit in commits:
        for prefix, prefix_release_type in PREFIXES.items():
            if commit.startswith(f"{prefix}: "):
                # Check whether this is greater than the existing value
                if release_type.value < prefix_release_type.value:
                    release_type = prefix_release_type
    return release_type


def get_biggest_tag(tags: List[str]):
    pattern = r"^v\d+\.\d+\.\d+$"
    max_version = (0, 1, 0)
    for tag in tags:
        if re.match(pattern, tag):
            # This tag has valid format (vX.Y.Z)
            major, minor, patch = tag.replace("v", "").split(".")
            major = int(major)
            minor = int(minor)
            patch = int(patch)
            if (
                major > max_version[0]
                or (major == max_version[0] and minor > max_version[1])
                or (
                    major == max_version[0]
                    and minor == max_version[1]
                    and patch > max_version[2]
                )
            ):
                max_version = (major, minor, patch)
    return f"v{max_version[0]}.{max_version[1]}.{max_version[2]}"


def compute_next_version(release_type: ReleaseType, tags: List[str]) -> str:
    """."""
    if len(tags) < 1:
        return "v0.1.0"
    major, minor, patch = get_biggest_tag(tags).replace("v", "").split(".")
    max_version = (int(major), int(minor), int(patch))
    if release_type == ReleaseType.MAJOR:
        max_version = (max_version[0] + 1, 0, 0)
    elif release_type == ReleaseType.MINOR:
        max_version = (max_version[0], max_version[1] + 1, 0)
    elif release_type == ReleaseType.PATCH:
        max_version = (max_version[0], max_version[1], max_version[2] + 1)
    else:
        pass  # NO_RELEASE

    return f"v{max_version[0]}.{max_version[1]}.{max_version[2]}"


def apply_tag(existing_tags: List[str], new_tag: str):
    if new_tag not in existing_tags:
        print(f"Tagging/pushing new tag: {new_tag}")
        new_tag_stripped = new_tag.replace("v", "")
        commands = [
            f'sed "s/^version = \\"[0-9]\\+\\.[0-9]\\+\\.[0-9]\\"/version = \\"{new_tag_stripped}\\"/" cargo.toml'
            f'sed -i "s/\\"version\\": \\"[0-9]\\+\\.[0-9]\\+\\.[0-9]\\"/\\"version\\": \\"{new_tag_stripped}\\"/" package.json'
            f"git config --global user.email semver@pagekey.io",
            f'git config --global user.name "PageKey Semver"',
            f"git add --all",
            f"git commit -m '{new_tag}'",
            f"git tag {new_tag}",
            f"git push origin {new_tag}",
        ]
        for command in commands:
            print("Running:", command)
            os.system(command)
    else:
        print(f"Tag {new_tag} already exists - skipping tag/push.")
