"""Module for dynamically importing Python objects."""

import importlib
import os
import sys
from typing import Any


def dynamic_import(path: str) -> Any:
    """Import a Python object from a module import path.

    Note that this function automatically adds the current directory to `sys.path`,
    which allows `.py` files in the current directory to be imported.

    Args:
        path: A string representing a module import.
            A colon is used to separate the module from the object with it being imported.
            Example: "shutil:rmtree" will import the rmtree function from the shutil module and return it.

    Returns:
        The object represented by the "path" arg.

    Raises:
        ImportError, AttributeError if the import string is not valid.
    """
    # Include .py files in the current directory.
    sys.path.insert(0, os.getcwd())
    module_path, class_name = path.split(":")
    module = importlib.import_module(module_path)
    return getattr(module, class_name)
