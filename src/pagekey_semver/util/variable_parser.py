

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
        if part3 is None:
            map[part1] = part2
        else:
            map.setdefault(part1, {}).setdefault(part2, {})
        return map

    def get_config(self):
        result = {}
        current_dict = result
        for variable in self._variables:
            parts = variable.split("__")
            for index, part1 in enumerate(parts):
                is_last_part = index == len(parts) - 1
                if is_last_part:
                    part2 = None
                    part3 = None
                else:
                    part2 = parts[index + 1]
                    is_second_to_last = index == len(parts) - 2
                    if is_second_to_last:
                        part3 = None
                    else:
                        part3 = parts[index + 2]
                current_dict = self.apply_parts(current_dict, part1, part2, part3)
        # Manually re-arrange config items that are lists
        if "prefixes" in result:
            new_prefixes = []
            for key, value in enumerate(result["prefixes"]):
                new_prefixes.append(Prefix(label=key, type=value))
            result["prefixes"] = new_prefixes
        return result
