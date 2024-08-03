from typing import Any


def get_dict_value(d: dict, path: str, sep: str = ".") -> Any:
    """
    Retrieve a value from a nested dictionary using a dot-separated (or other separator) string path.

    Args:
        d: The dictionary to retrieve the value from.
        path: The path string specifying the keys, separated by the given separator.
        sep: The separator used in the path string. Defaults to ".".

    Returns:
        The value from the dictionary at the specified path.

    Raises:
        KeyError: If any of the keys in the path do not exist in the dictionary.
    """
    keys = path.split(sep)
    for key in keys:
        d = d[key]
    return d


def set_dict_value(d: dict, path: str, value: Any, sep: str = ".") -> None:
    """
    Set a value in a nested dictionary using a dot-separated (or other separator) string path.

    Args:
        d (dict): The dictionary to set the value in.
        path (str): The path string specifying the keys, separated by the given separator.
        value: The value to set at the specified path.
        sep (str): The separator used in the path string. Defaults to ".".

    Returns:
        None. The function modifies the dictionary in place.

    Raises:
        TypeError: If the intermediate values in the path are not dictionaries.
    """
    keys = path.split(sep)
    for key in keys[:-1]:
        d = d.setdefault(key, {})
    d[keys[-1]] = value
