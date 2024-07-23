from unittest.mock import call, patch, MagicMock, mock_open

from pagekey_semver.lib import (
    Commit,
    get_git_tags,
    get_commit_messages_since,
    ReleaseType,
    compute_release_type,
    compute_next_version,
    apply_tag,
    get_biggest_tag,
    update_changelog,
)


MODULE_UNDER_TEST = "pagekey_semver.lib"


@patch("subprocess.run")
def test_get_git_tags_with_no_fail_returns_list_of_tags(mock_run):
    # Arrange.
    mock_result = MagicMock()
    mock_result.stdout = "tag1\ntag2"
    mock_run.return_value = mock_result

    # Act.
    result = get_git_tags()

    # Assert.
    mock_run.assert_called_with(
        "git tag".split(),
        check=True,
        stdout=-1,
        stderr=-1,
        text=True,
    )
    assert result[0] == "tag1"
    assert result[1] == "tag2"


@patch("subprocess.run")
def test_get_commit_messages_since_with_valid_hash_returns_list_of_messages(mock_run):
    # Arrange.
    mock_result = MagicMock()
    mock_result.stdout = "aaaaa1 Do something\naaaaa2 Do something else"
    mock_run.return_value = mock_result

    # Act.
    result = get_commit_messages_since("HEAD~2")

    # Assert.
    mock_run.assert_called_with(
        [
            "git",
            "log",
            "HEAD~2..HEAD",
            "--pretty=format:%H %s",
        ],
        check=True,
        stdout=-1,
        stderr=-1,
        text=True,
    )
    assert result[0].hash == "aaaaa1"
    assert result[0].message == "Do something"
    assert result[1].hash == "aaaaa2"
    assert result[1].message == "Do something else"


def test_compute_release_type_with_no_prefixes_returns_no_release():
    # Arrange.
    commits = [
        Commit(hash="aaaaa1", message="nothing important"),
        Commit(hash="aaaaa2", message="another poorly formatted commit message"),
    ]
    # Act.
    result = compute_release_type(commits)
    # Assert.
    assert result == ReleaseType.NO_RELEASE


def test_compute_release_type_with_only_fix_returns_patch():
    # Arrange.
    commits = [
        Commit(hash="aaaaa1", message="fix: Somewhat important"),
        Commit(hash="aaaaa2", message="another poorly formatted commit message"),
    ]
    # Act.
    result = compute_release_type(commits)
    # Assert.
    assert result == ReleaseType.PATCH


def test_compute_release_type_with_fix_and_feat_returns_minor():
    # Arrange.
    commits = [
        Commit(hash="aaaaa1", message="fix: Somewhat important"),
        Commit(hash="aaaaa2", message="feat: another poorly formatted commit message"),
    ]
    # Act.
    result = compute_release_type(commits)
    # Assert.
    assert result == ReleaseType.MINOR


def test_compute_release_type_with_major_returns_major():
    # Arrange.
    commits = [
        Commit(hash="aaaaa1", message="fix: Somewhat important"),
        Commit(hash="aaaaa2", message="feat: Add something"),
        Commit(hash="aaaaa2", message="major: Wow this is a big deal"),
    ]
    # Act.
    result = compute_release_type(commits)
    # Assert.
    assert result == ReleaseType.MAJOR


def test_get_biggest_tag_with_list_of_tags_returns_biggest_tag():
    # Arrange.
    tags = ["v0.2.0", "v0.3.0", "v1.2.3", "v1.0.0"]
    # Act.
    result = get_biggest_tag(tags)
    # Assert.
    assert result == "v1.2.3"


def test_compute_next_version_with_no_existing_tags_returns_default_value():
    # Arrange.
    release_type = ReleaseType.MAJOR
    tags = []
    # Act.
    result = compute_next_version(release_type, tags)
    # Assert.
    assert result == "v0.1.0"


def test_compute_next_version_with_no_release_returns_greatest_tag():
    # Arrange.
    release_type = ReleaseType.NO_RELEASE
    tags = ["v0.1.0", "v0.3.0", "v0.2.0", "unrelated-tag"]
    # Act.
    result = compute_next_version(release_type, tags)
    # Assert.
    assert result == "v0.3.0"


def test_compute_next_version_with_patch_bumps_patch_value():
    # Arrange.
    release_type = ReleaseType.PATCH
    tags = ["v0.1.0", "v0.3.2", "v0.2.0", "unrelated-tag"]
    # Act.
    result = compute_next_version(release_type, tags)
    # Assert.
    assert result == "v0.3.3"


def test_compute_next_version_with_minor_bumps_minor_value():
    # Arrange.
    release_type = ReleaseType.MINOR
    tags = ["v0.1.0", "v0.3.2", "v0.2.0", "unrelated-tag"]
    # Act.
    result = compute_next_version(release_type, tags)
    # Assert.
    assert result == "v0.4.0"


def test_compute_next_version_with_major_bumps_major_value():
    # Arrange.
    release_type = ReleaseType.MAJOR
    tags = ["v0.1.0", "v0.3.2", "v0.2.0", "unrelated-tag"]
    # Act.
    result = compute_next_version(release_type, tags)
    # Assert.
    assert result == "v1.0.0"


@patch("subprocess.run")
def test_apply_tag_with_existing_tag_does_nothing(mock_run):
    # Arrange.
    existing_tags = ["v0.1.0", "v3.0.0", "v2.0.0"]
    new_tag = "v3.0.0"

    # Act.
    result = apply_tag(existing_tags, new_tag)

    # Assert.
    mock_run.assert_not_called()


@patch("os.system")
def test_apply_tag_with_new_tag_tags_and_pushes(mock_system):
    # Arrange.
    existing_tags = ["v0.1.0", "v3.0.0", "v2.0.0"]
    new_tag = "v4.0.0"
    new_tag_stripped = new_tag.replace("v", "")
    mock_system.return_value = 0  # exit code

    # Act.
    apply_tag(existing_tags, new_tag)

    # Assert.
    commands = [
        f'sed -i -E "s/^version = \\"[0-9]+\\.[0-9]+\\.[0-9]+\\"/version = \\"{new_tag_stripped}\\"/" Cargo.toml',
        f'sed -i -E "s/\\"version\\": \\"[0-9]+\\.[0-9]+\\.[0-9]+\\"/\\"version\\": \\"{new_tag_stripped}\\"/" package.json',
        f"git config --global user.email semver@pagekey.io",
        f'git config --global user.name "PageKey Semver"',
        f"git add --all",
        f"git commit -m '{new_tag}'",
        f"git tag {new_tag}",
        f"git push origin {new_tag}",
    ]
    mock_system.assert_has_calls(
        [
            call(command)
            for command in commands
        ]
    )


@patch('builtins.open', new_callable=mock_open)
def test_update_changelog_with_commits_updates_changelog_file(mock_open):
    # Arrange.
    version = "v1.0.0"
    commits = [
        Commit(hash="aaaaa1", message="my commit"),
        Commit(hash="aaaaa2", message="fix: Do something somewhat important"),
        Commit(hash="aaaaa3", message="feat: Add something"),
        Commit(hash="aaaaa4", message="random commit"),
        Commit(hash="aaaaa5", message="major: Wow this is a big deal"),
        Commit(hash="aaaaa6", message="some other commit"),
    ]
    mock_file = mock_open.return_value

    # Act.
    update_changelog(version, commits)

    # Assert.
    mock_open.assert_called_with("CHANGELOG.md", "a")
    mock_file.write.assert_has_calls([
        call(f"## {version}\n\n"),
        call("- fix: Do something somewhat important (aaaaa2)\n"),
        call("- feat: Add something (aaaaa3)\n"),
        call("- major: Wow this is a big deal (aaaaa5)\n"),
        call("\n"),
    ])
