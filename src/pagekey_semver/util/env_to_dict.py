"""Module to convert env vars to a dict."""

from typing import Dict


VARIABLE_PREFIX = "SEMVER_"


def convert_env_to_dict(variables: Dict[str, str]) -> Dict:
    """Convert variables dict to config dict.

    This function takes a list of flattened config items and
    re-hydrates them into a valid config dict.

    To learn more about the expected inputs and outputs, check out the tests for this function or the docs.

    Args:
        variables: Dict with keys/values that represent environment variables.

    Returns:
        Dictionary that can be parsed into a valid SemverConfig object.
    """
    # Filter irrelevant vars and get rid of prefix.
    variables = {
        key.replace(VARIABLE_PREFIX, ""): variables[key]
        for key in variables
        if key.startswith(VARIABLE_PREFIX)
    }

    result = {}

    # Parse each environment variable.
    for variable, value in variables.items():
        parts = variable.split("__")
        # Create a nested dictionary structure
        d = result
        for part in parts[:-1]:
            if part not in d:
                d[part] = {}
            d = d[part]

        # Set the final key's value
        d[parts[-1]] = value

    # Manually re-arrange config items that are lists
    if "prefixes" in result:
        new_prefixes = []
        for key, value in result["prefixes"].items():
            new_prefixes.append(
                {
                    "label": key,
                    "type": value,
                }
            )
        result["prefixes"] = new_prefixes
    if "file_replacers" in result:
        # Simply discard the keys to convert to list.
        new_file_replacers = list(result["file_replacers"].values())
        result["file_replacers"] = new_file_replacers

    return result
