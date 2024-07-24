"""Test release module."""
from pagekey_semver.release import Commit, ReleaseType, compute_next_version, compute_release_type, get_biggest_tag


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
