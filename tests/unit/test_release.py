"""Test release module."""
import pytest
from pagekey_semver.config import DEFAULT_CONFIG, DEFAULT_CONFIG_DICT
from pagekey_semver.models import SemverConfig
from pagekey_semver.release import Commit, ReleaseType, SemverRelease, Tag, release_greater


@pytest.mark.parametrize("a, b, expected", [
    (ReleaseType.NO_RELEASE, ReleaseType.NO_RELEASE, False),
    (ReleaseType.NO_RELEASE, ReleaseType.PATCH, True),
    (ReleaseType.NO_RELEASE, ReleaseType.MINOR, True),
    (ReleaseType.NO_RELEASE, ReleaseType.MAJOR, True),
    
    (ReleaseType.PATCH, ReleaseType.NO_RELEASE, False),
    (ReleaseType.PATCH, ReleaseType.PATCH, False),
    (ReleaseType.PATCH, ReleaseType.MINOR, True),
    (ReleaseType.PATCH, ReleaseType.MAJOR, True),

    (ReleaseType.MINOR, ReleaseType.NO_RELEASE, False),
    (ReleaseType.MINOR, ReleaseType.PATCH, False),
    (ReleaseType.MINOR, ReleaseType.MINOR, False),
    (ReleaseType.MINOR, ReleaseType.MAJOR, True),

    (ReleaseType.MAJOR, ReleaseType.NO_RELEASE, False),
    (ReleaseType.MAJOR, ReleaseType.PATCH, False),
    (ReleaseType.MAJOR, ReleaseType.MINOR, False),
    (ReleaseType.MAJOR, ReleaseType.MAJOR, False),
])
def test_release_greater_with_releasetype_returns_valid_result(a, b, expected):
    # Act.
    result = release_greater(a, b)
    
    # Assert.
    assert result == expected


class TestSemverRelease:

    class Test_compute_release_type:
        def test_with_no_prefixes_returns_no_release(self):
            # Arrange.
            commits = [
                Commit(hash="aaaaa1", message="nothing important"),
                Commit(hash="aaaaa2", message="another poorly formatted commit message"),
            ]
            release = SemverRelease(DEFAULT_CONFIG)
            # Act.
            result = release.compute_release_type(commits)
            # Assert.
            assert result == ReleaseType.NO_RELEASE


        def test_with_only_fix_returns_patch(self):
            # Arrange.
            commits = [
                Commit(hash="aaaaa1", message="fix: Somewhat important"),
                Commit(hash="aaaaa2", message="another poorly formatted commit message"),
            ]
            release = SemverRelease(DEFAULT_CONFIG)
            # Act.
            result = release.compute_release_type(commits)
            # Assert.
            assert result == ReleaseType.PATCH


        def test_with_fix_and_feat_returns_minor(self):
            # Arrange.
            commits = [
                Commit(hash="aaaaa1", message="fix: Somewhat important"),
                Commit(hash="aaaaa2", message="feat: another poorly formatted commit message"),
            ]
            release = SemverRelease(DEFAULT_CONFIG)
            # Act.
            result = release.compute_release_type(commits)
            # Assert.
            assert result == ReleaseType.MINOR


        def test_with_major_returns_major(self):
            # Arrange.
            commits = [
                Commit(hash="aaaaa1", message="fix: Somewhat important"),
                Commit(hash="aaaaa2", message="feat: Add something"),
                Commit(hash="aaaaa2", message="major: Wow this is a big deal"),
            ]
            release = SemverRelease(DEFAULT_CONFIG)
            # Act.
            result = release.compute_release_type(commits)
            # Assert.
            assert result == ReleaseType.MAJOR

    class Test_get_matching_tags:

        TEST_TAGS = [
            "v0.1.0",
            "b1.2.3",
            "2.0.0",
            "ver_3-1-4",
            "unrelated",
        ]
        @pytest.mark.parametrize("format, expected_matches", [
            ("v%M.%m.%p", [Tag(name="v0.1.0", major=0, minor=1, patch=0)]),
            ("v%m.%M.%p", [Tag(name="v0.1.0", major=1, minor=0, patch=0)]),
            ("b%M.%m.%p", [Tag(name="b1.2.3", major=1, minor=2, patch=3)]),
            ("%M.%m.%p", [Tag(name="2.0.0", major=2, minor=0, patch=0)]),
            ("ver_%M-%m-%p", [Tag(name="ver_3-1-4", major=3, minor=1, patch=4)]),
        ])
        def test_with_various_formats_matches(self, format, expected_matches):
            # Arrange.
            config = SemverConfig(**{**DEFAULT_CONFIG_DICT, "format": format})
            release = SemverRelease(config)

            # Act.
            actual_matches = release.get_matching_tags(self.TEST_TAGS)

            # Assert.
            assert expected_matches == actual_matches


    class Test_get_biggest_tag:
        def test_with_list_of_tags_returns_biggest_tag(self):
            # Arrange.
            tags = [
                "v0.2.0",
                "v0.3.0",
                "v1.2.3",
                "v1.0.0",
            ]
            release = SemverRelease(DEFAULT_CONFIG)
            # Act.
            result = release.get_biggest_tag(tags)
            # Assert.
            assert result == Tag(tags[2], 1, 2, 3)


        def test_with_custom_tag_format_returns_biggest_tag(self):
            # Arrange.
            tags = ["v0.2.0", "v0.3.0", "v1.2.3", "v1.0.0"]
            tags = ["ver_0-2-0", "ver_0-3-0", "ver_1-2-3", "ver_1-0-0", "unrelated"]
            format = "ver_%M-%m-%p"
            config = SemverConfig(**{**DEFAULT_CONFIG_DICT, "format": format})
            release = SemverRelease(config)
            # Act.
            result = release.get_biggest_tag(tags)
            # Assert.
            assert result == Tag("ver_1-2-3", 1, 2, 3)

    class Test_compute_next_version:
        def test_with_no_existing_tags_returns_default_value(self):
            # Arrange.
            release_type = ReleaseType.MAJOR
            tags = []
            release = SemverRelease(DEFAULT_CONFIG)
            # Act.
            result = release.compute_next_version(release_type, tags)
            # Assert.
            assert result == Tag("v0.1.0", 0, 1, 0)


        def test_with_no_release_returns_none(self):
            # Arrange.
            release_type = ReleaseType.NO_RELEASE
            tags = ["v0.1.0", "v0.3.0", "v0.2.0", "unrelated-tag"]
            release = SemverRelease(DEFAULT_CONFIG)
            # Act.
            result = release.compute_next_version(release_type, tags)
            # Assert.
            assert result == Tag("v0.3.0", 0, 3, 0)


        def test_with_patch_bumps_patch_value(self):
            # Arrange.
            release_type = ReleaseType.PATCH
            tags = ["v0.1.0", "v0.3.2", "v0.2.0", "unrelated-tag"]
            release = SemverRelease(DEFAULT_CONFIG)
            # Act.
            result = release.compute_next_version(release_type, tags)
            # Assert.
            assert result == Tag("v0.3.3", 0, 3, 3)


        def test_with_minor_bumps_minor_value(self):
            # Arrange.
            release_type = ReleaseType.MINOR
            tags = ["v0.1.0", "v0.3.2", "v0.2.0", "unrelated-tag"]
            release = SemverRelease(DEFAULT_CONFIG)
            # Act.
            result = release.compute_next_version(release_type, tags)
            # Assert.
            assert result == Tag("v0.4.0", 0, 4, 0)


        def test_with_major_bumps_major_value(self):
            # Arrange.
            release_type = ReleaseType.MAJOR
            tags = ["v0.1.0", "v0.3.2", "v0.2.0", "unrelated-tag"]
            release = SemverRelease(DEFAULT_CONFIG)
            # Act.
            result = release.compute_next_version(release_type, tags)
            # Assert.
            assert result == Tag("v1.0.0", 1, 0, 0)

        def test_with_custom_tag_works(self):
            # Arrange.
            release_type = ReleaseType.MAJOR
            tags = ["ver_0-1-0", "ver_0-3-2", "ver_0-2-0", "unrelated-tag"]
            format = "ver_%M-%m-%p"
            config = SemverConfig(**{**DEFAULT_CONFIG_DICT, "format": format})
            release = SemverRelease(config)
            # Act.
            result = release.compute_next_version(release_type, tags)
            # Assert.
            assert result == Tag("ver_1-0-0", 1, 0, 0)
