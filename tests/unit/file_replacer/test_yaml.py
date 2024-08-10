"""Module to test YAML file replacer."""

from unittest.mock import mock_open, patch
from pagekey_semver.models import Tag
from pagekey_semver.file_replacer.yaml import YamlFileReplacer


MODULE_UNDER_TEST = "pagekey_semver.file_replacer.yaml"


class TestYamlFileReplacer:
    class Test_perform_replace:
        @patch(f"{MODULE_UNDER_TEST}.yaml")
        @patch("builtins.open", new_callable=mock_open)
        def test_with_simple_tag_uses_format_to_replace(
            self, mock_builtins_open, mock_yaml
        ):
            # Arrange.
            tag = Tag("v4.0.0", 4, 0, 0)
            replacer = YamlFileReplacer(
                name="some_file.yaml",
                key="version",
                format="%M.%m.%p",
            )
            mock_yaml.safe_load.return_value = {
                "version": "to be replaced",
                "other_key": "untouched",
            }

            # Act.
            replacer.perform_replace(tag)

            # Assert.
            mock_builtins_open.assert_any_call("some_file.yaml", "r")
            mock_builtins_open.assert_any_call("some_file.yaml", "w")
            mock_yaml.safe_load.assert_called_once()
            mock_yaml.dump.assert_called_once()
            assert mock_yaml.dump.call_args_list[0][0][0] == {
                "version": "4.0.0",
                "other_key": "untouched",
            }

        @patch(f"{MODULE_UNDER_TEST}.yaml")
        @patch("builtins.open", new_callable=mock_open)
        def test_with_nested_tag_uses_format_to_replace(
            self, mock_builtins_open, mock_yaml
        ):
            # Arrange.
            tag = Tag("v4.0.0", 4, 0, 0)
            replacer = YamlFileReplacer(
                name="some_file.yaml",
                key="project.metadata.version",
                format="%M.%m.%p",
            )
            mock_yaml.safe_load.return_value = {
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
            mock_builtins_open.assert_any_call("some_file.yaml", "r")
            mock_builtins_open.assert_any_call("some_file.yaml", "w")
            mock_yaml.safe_load.assert_called_once()
            mock_yaml.dump.assert_called_once()
            assert mock_yaml.dump.call_args_list[0][0][0] == {
                "project": {
                    "metadata": {
                        "version": "4.0.0",
                    },
                },
                "other_key": "untouched",
            }
