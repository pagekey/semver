import pytest

from src.pagekey_semver.config import DEFAULT_CONFIG_DICT
from src.pagekey_semver.util.variable_parser import VariableParser


class TestVariableParser:

    class Test_get_all_prefixed_env_vars:
        
        @pytest.mark.parametrize("vars, expected", [
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
                    "SEMVER_replace_files__0": "testing",
                    "SOME_OTHER_VAR": "irrelevant"
                },
                {
                    "SEMVER_changelog_path": "CHANGELOG.md",
                    "SEMVER_git__name": "me",
                    "SEMVER_replace_files__0": "testing",
                }
            ),
        ])
        def test_with_env_vars_returns_prefixed_vars(self, vars, expected):
            # Arrange.
            parser = VariableParser(vars)

            # # Act.
            # result = parser.get_all_prefixed_vars()

            # # Assert.
            # assert result == expected

    class Test_convert_env_prefixes_to_dict:

        def test_with_sample_values_works(self):
            # Arrange.
            parser = VariableParser({
                    "SEMVER_changelog_path": "CHANGELOG.md",
                    "SEMVER_git__name": "me",
                    "SEMVER_replace_files__0__type": "json",
                    "SEMVER_replace_files__0__key": "version",
            })
            
            # Act.
            # result = parser.convert_env_prefixes_to_dict()

            # Assert.
            # assert result == {
            #     "changelog_path": "CHANGELOG.md",
            #     "git": {
            #         "name": "me",
            #     },
            #     "replace_files": [
            #         {
            #             "type": "json",
            #             "key": "version",
            #         },
            #     ],
            # }


    class Test_get_config:

        def test_with_no_env_vars_set_returns_same_dict(self):
            # Arrange.
            parser = VariableParser({})
            
            # Act.
            # parser.apply_env_to_config_dict(DEFAULT_CONFIG_DICT)
            
            # Assert.
            pass


# @patch('os.getenv')
# @patch('builtins.open', new_callable=mock_open)
# def test_load_config_with_env_vars_for_git_user_parses_config(mock_builtin_open, mock_getenv):
#     # Arrange.
#     mock_getenv.side_effect = [
#         "git_user",
#         "git@email.com",
#     ]
#     mock_path = MagicMock()
#     mock_path.is_file.return_value = True
#     mock_file = mock_builtin_open.return_value
#     mock_file.read.return_value = yaml.safe_dump({
#         "git": {
#             "name": "$GIT_USER",
#             "email": "$GIT_EMAIL",
#         },
#     })

#     # Act.
#     config = load_config(mock_path)

#     # Assert.
#     mock_getenv.assert_has_calls([
#         call("GIT_USER"),
#         call("GIT_EMAIL"),
#     ])
#     assert config.git.name == "git_user"
#     assert config.git.email == "git@email.com"
