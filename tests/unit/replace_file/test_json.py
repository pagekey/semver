"""Module to test JSON file replacer."""

from unittest.mock import mock_open, patch
from pagekey_semver.models import Tag
from pagekey_semver.replace_file.json import JsonReplaceFile


MODULE_UNDER_TEST = "pagekey_semver.replace_file.json"

class TestJsonReplaceFile:
    class Test_perform_replace:

        @patch(f"{MODULE_UNDER_TEST}.json")
        @patch("builtins.open", new_callable=mock_open)
        def test_with_simple_tag_uses_format_to_replace(self, mock_builtins_open, mock_json):
            # Arrange.
            tag = Tag("v4.0.0", 4, 0, 0)
            replacer = JsonReplaceFile(
                name="some_file.json",
                key="version",
                format="%M.%m.%p",
            )
            mock_json.load.return_value = {
                "version": "to be replaced",
                "other_key": "untouched",
            }

            # Act.
            replacer.perform_replace(tag)

            # Assert.
            mock_builtins_open.assert_any_call("some_file.json", "r")
            mock_builtins_open.assert_any_call("some_file.json", "w")
            mock_json.load.assert_called_once()
            mock_json.dump.assert_called_once()
            assert mock_json.dump.call_args_list[0][0][0] == {
                "version": "4.0.0",
                "other_key": "untouched",
            }

        @patch(f"{MODULE_UNDER_TEST}.json")
        @patch("builtins.open", new_callable=mock_open)
        def test_with_nested_tag_uses_format_to_replace(self, mock_builtins_open, mock_json):
            # Arrange.
            tag = Tag("v4.0.0", 4, 0, 0)
            replacer = JsonReplaceFile(
                name="some_file.json",
                key="project.metadata.version",
                format="%M.%m.%p",
            )
            mock_json.load.return_value = {
                "project": {
                    "metadata": {
                        "version": "to be replaced",
                    },
                },
                "other_key": "untouched",
            }

            # Act.
            replacer.perform_replace(tag)

            # Assert.
            mock_builtins_open.assert_any_call("some_file.json", "r")
            mock_builtins_open.assert_any_call("some_file.json", "w")
            mock_json.load.assert_called_once()
            mock_json.dump.assert_called_once()
            assert mock_json.dump.call_args_list[0][0][0] == {
                "project": {
                    "metadata": {
                        "version": "4.0.0",
                    },
                },
                "other_key": "untouched",
            }
