

import os
from typing import Dict


VARIABLE_PREFIX = "SEMVER_"

class VariableParser:

    def __init__(self, variables: Dict[str, str]):
        # Filter out irrelevant variables.
        self._variables = {
            key: variables[key]
            for key in variables
            if key.startswith("SEMVER_")
        }

    def convert_prefixed_vars_to_config_dict(self, prefixed_vars: Dict[str, str]) -> dict:
        result = {}

        for key, value in prefixed_vars.items():
            parts = key.split("__")
            current_dict = result

            for part in parts[:-1]:
                if part.isdigit():
                    part = int(part)
                    if not isinstance(current_dict, list):
                        current_dict = current_dict.setdefault()

        for prefix, value in prefixed_vars.items():
            prefix = prefix.replace("SEMVER_", "")
            fields = prefix.split("__")
            cur_dict = result
            for field in fields[0:-1]:
                is_list = False
                try:
                    int(field)
                    is_list = True
                except ValueError:
                    pass
                if is_list:
                    if field not in cur_dict:
                        cur_dict[field] = []
                    while len(cur_dict[field]) < int(field):
                        cur_dict[field].append(None)
                    cur_dict[field]
                else:
                    if field not in cur_dict:
                        cur_dict[field] = {}
                cur_dict = cur_dict[field]
            cur_dict[fields[-1]] = value
        return result

    def get_config(self):
        # prefixed_vars = self.get_all_prefixed_vars()
        # config_from_prefixed_vars = self.convert_prefixed_vars_to_config_dict(prefixed_vars)
        return {}
