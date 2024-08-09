"""Test update_dict module."""

import pytest

from pagekey_semver.util.update_dict import get_dict_value, merge_dicts, set_dict_value


@pytest.fixture
def sample_dict():
    return {"project": {"metadata": {"version": "1.0.0"}}}


class Test_get_dict_value:
    def test_with_default_separator_returns_value(self, sample_dict):
        # Arrange
        d = sample_dict
        path = "project.metadata.version"

        # Act
        result = get_dict_value(d, path)

        # Assert
        assert result == "1.0.0"

    def test_with_custom_separator_returns_value(self):
        # Arrange
        d = {"a": {"b": {"c": 10}}}
        path = "a|b|c"
        sep = "|"

        # Act
        result = get_dict_value(d, path, sep)

        # Assert
        assert result == 10


class Test_set_dict_value:
    def test_with_existing_key_updates_value(self, sample_dict):
        # Arrange
        d = sample_dict
        path = "project.metadata.version"
        value = "2.0.0"

        # Act
        set_dict_value(d, path, value)

        # Assert
        assert d["project"]["metadata"]["version"] == "2.0.0"

    def test_with_nonexistant_key_creates_new_key(self, sample_dict):
        # Arrange
        d = sample_dict
        path = "project.metadata.new_version"
        value = "3.0.0"

        # Act
        set_dict_value(d, path, value)

        # Assert
        assert d["project"]["metadata"]["new_version"] == "3.0.0"

    def test__with_blank_dict_creates_nested_keys(self):
        # Arrange
        new_dict = {}
        path = "a.b.c"
        value = 10

        # Act
        set_dict_value(new_dict, path, value)

        # Assert
        assert new_dict["a"]["b"]["c"] == 10

    def test_with_custom_separator_creates_keys_and_updates_value(self):
        # Arrange
        another_dict = {}
        path = "a|b|c"
        value = 20
        sep = "|"

        # Act
        set_dict_value(another_dict, path, value, sep)

        # Assert
        assert another_dict["a"]["b"]["c"] == 20


class Test_merge_dicts:
    def test_with_two_dicts_merges_values(self):
        # Arrange.
        d1 = {
            "git": {
                "name": "me",
            },
        }
        d2 = {
            "git": {
                "email": "me@email.com",
            },
            "other": "key",
        }

        # Act.
        result = merge_dicts(d1, d2)

        # Assert.
        assert result == {
            "git": {
                "name": "me",
                "email": "me@email.com",
            },
            "other": "key",
        }
