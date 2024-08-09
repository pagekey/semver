"""Module for functions that modify dicts."""

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


def merge_dicts(d1: dict, d2: dict) -> dict:
    """
    Merges two dictionaries recursively. If both dictionaries contain a key
    with a dictionary as its value, the function will recursively merge the
    sub-dictionaries. If a key exists in both dictionaries but the corresponding
    values are not dictionaries, the value from the second dictionary (d2)
    will overwrite the value from the first dictionary (d1).

    Args:
        d1 (dict): The first dictionary to merge.
        d2 (dict): The second dictionary to merge.

    Returns:
        dict: A new dictionary that is the result of merging d1 and d2.
    """
    # Start with a copy of the first dictionary
    merged = d1.copy()

    for key, value in d2.items():
        if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
            # If both d1 and d2 have the same key and the value is a dict, merge them recursively
            merged[key] = merge_dicts(merged[key], value)
        else:
            # Otherwise, just set the value from d2
            merged[key] = value

    return merged
