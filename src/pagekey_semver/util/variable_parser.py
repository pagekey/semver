

import os
from typing import Dict

from pagekey_semver.models import Prefix


VARIABLE_PREFIX = "SEMVER_"

class VariableParser:

    def __init__(self, variables: Dict[str, str]):
        # Filter out irrelevant variables.
        self._variables = {
            key.replace(VARIABLE_PREFIX, ""): variables[key]
            for key in variables
            if key.startswith(VARIABLE_PREFIX)
        }

    def apply_parts(self, map, part1, part2, part3):

        return map

    def get_config(self):
        result = {}
        
        for variable, value in self._variables.items():
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
                new_prefixes.append({
                    "label": key,
                    "type": value,
                })
            result["prefixes"] = new_prefixes
        if "replace_files" in result:
            # Simply discard the keys to convert to list.
            new_replace_files = list(result["replace_files"].values())
            result["replace_files"] = new_replace_files

        return result
