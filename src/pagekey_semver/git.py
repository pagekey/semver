"""Module for interacting with Git."""
import os
import subprocess
from typing import List
from pagekey_semver.config import DEFAULT_CONFIG, SemverConfig
from pagekey_semver.release import Commit


class GitManager:
    pass

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
        print(f"Error getting git tags: {e.stderr}", flush=True)
        return []


def get_commit_messages_since(commit_hash) -> List[Commit]:
    """."""
    try:
        result = subprocess.run(
            ["git", "log", f"{commit_hash}..HEAD", "--pretty=format:%H %s"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        # Split the output into lines (each line is a commit message)
        commit_lines = result.stdout.strip().split("\n")
        commits = []
        for line in commit_lines:
            hash = line.split()[0]
            message = line.replace(hash + ' ', '')
            commits.append(Commit(hash, message))
        return commits
    except subprocess.CalledProcessError as e:
        print(f"Error getting commit messages: {e.stderr}", flush=True)
        return []


def apply_tag(existing_tags: List[str], new_tag: str, config: SemverConfig = DEFAULT_CONFIG):
    if new_tag not in existing_tags:
        print(f"Tagging/pushing new tag: {new_tag}", flush=True)
        new_tag_stripped = new_tag.replace("v", "")
        commands = [
            f'sed -i -E "s/^version = \\"[0-9]+\\.[0-9]+\\.[0-9]+\\"/version = \\"{new_tag_stripped}\\"/" Cargo.toml',
            f'sed -i -E "s/\\"version\\": \\"[0-9]+\\.[0-9]+\\.[0-9]+\\"/\\"version\\": \\"{new_tag_stripped}\\"/" package.json',
            f"git config user.email {config.git.email}",
            f'git config user.name "{config.git.name}"',
            f"git add --all",
            f"git commit -m '{new_tag}'",
            f"git tag {new_tag}",
            f"git push origin {new_tag}",
            f"git push origin HEAD",
        ]
        for command in commands:
            print("Running:", command, flush=True)
            exit_code = os.system(command)
            if exit_code != 0:
                raise ValueError(f"Command failed: {command}")
    else:
        print(f"Tag {new_tag} already exists - skipping tag/push.", flush=True)
