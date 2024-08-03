from unittest.mock import patch
import pytest

from pagekey_semver.util.dynamic_import import dynamic_import


MODULE_UNDER_TEST = "pagekey_semver.util.dynamic_import"



@patch(f"{MODULE_UNDER_TEST}.os")
@patch(f"{MODULE_UNDER_TEST}.sys")
def test_dynamic_import_with_valid_import_returns_module(mock_sys, mock_os):
    # Arrange.
    path = "pagekey_semver.util.dynamic_import:dynamic_import"
    cwd = mock_os.getcwd.return_value
    
    # Act.
    result = dynamic_import(path)
    
    # Assert.
    assert result == dynamic_import
    mock_os.getcwd.assert_called_with()
    mock_sys.path.insert.assert_called_with(0, cwd)


def test_dynamic_import_with_invalid_import_raises_importerror():
    # Arrange.
    path = "non_existent_package.non_existent_module:NonExistentClass"
    
    # Act and Assert.
    with pytest.raises((ImportError, AttributeError)):
        dynamic_import(path)
