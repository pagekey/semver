import pytest

from src.pagekey_semver.util.variable_parser import VariableParser


class TestVariableParser:


    class Test_get_config:

        @pytest.mark.parametrize("variables, expected", [
            (
                {
                    "PATH": "something",
                    "TEST_VAR": "something else",
                },
                {}
            ),
            (
                {
                    "SEMVER_changelog_path": "CHANGELOG.md",
                    "SEMVER_git__name": "me",
                    "SEMVER_prefixes__testing": "minor",
                    "SEMVER_prefixes__testing2": "major",
                    "SEMVER_replace_files__0__name": "file.md",
                    "SEMVER_replace_files__0__type": "sed",
                    "SEMVER_replace_files__0__script": "pattern/pattern",
                    "SOME_OTHER_VAR": "irrelevant"
                },
                {
                    "changelog_path": "CHANGELOG.md",
                    "git": {
                        "name": "me",
                    },
                    "prefixes": [
                        {
                            "label": "testing",
                            "type": "minor",
                        },
                        {
                            "label": "testing2",
                            "type": "major",
                        },
                    ],
                    "replace_files": [
                        {
                            "type": "sed",
                            "name": "file.md",
                            "script": "pattern/pattern",
                        },
                    ],
                }
            ),
        ])
        def test_with_variables_converts_to_dict(self, variables, expected):
            # Arrange.
            parser = VariableParser(variables)
            
            # Act.
            config = parser.get_config()
            
            # Assert.
            assert config == expected
