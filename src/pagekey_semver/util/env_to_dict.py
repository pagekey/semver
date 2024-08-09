"""."""

from typing import Dict


VARIABLE_PREFIX = "SEMVER_"


def convert_env_to_dict(variables: Dict[str, str]) -> Dict:
    """."""
    # Filter irrelevant vars and get rid of prefix.
    variables = {
        key.replace(VARIABLE_PREFIX, ""): variables[key]
        for key in variables
        if key.startswith(VARIABLE_PREFIX)
    }

    result = {}

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
    if "replace_files" in result:
        # Simply discard the keys to convert to list.
        new_replace_files = list(result["replace_files"].values())
        result["replace_files"] = new_replace_files

    return result
