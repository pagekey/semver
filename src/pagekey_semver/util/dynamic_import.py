import importlib
import os
import sys


def dynamic_import(path):
    # Include .py files in the current directory.
    sys.path.insert(0, os.getcwd())
    module_path, class_name = path.split(":")
    module = importlib.import_module(module_path)
    return getattr(module, class_name)
