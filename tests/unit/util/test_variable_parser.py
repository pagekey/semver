import pytest

from src.pagekey_semver.util.variable_parser import VariableParser


class TestVariableParser:

    class Test_apply_parts:

        def test_with_last_value_sets_value(self):
            # Arrange.
            parser = VariableParser({})
            map = {}
            part1 = "something"
            part2 = "value"
            part3 = None

            # Act.
            result = parser.apply_parts(map, part1, part2, part3)

            # Assert.
            assert result == {
                "something": "value"
            }

        def test_with_all_values_creates_dicts(self):
            # Arrange.
            parser = VariableParser({})
            map = {}
            part1 = "something"
            part2 = "something_else"
            part3 = "value"

            # Act.
            result = parser.apply_parts(map, part1, part2, part3)

            # Assert.
            assert result == {
                "something": {
                    "something_else": {},
                }
            }



    class Test_get_config:

        @pytest.mark.skip()
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
                    "SEMVER_replace_files__testing": "minor",
                    "SEMVER_replace_files__testing2": "major",
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
                    # TODO replace files
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
