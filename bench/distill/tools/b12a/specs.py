"""Behavior specs for the b12a cases, merged into ../b12/behavior.py SPEC.
Each module keeps its own SPEC_* dict beside its builders."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
SPEC = {}
for _name in ("m9", "m10"):
    try:
        _mod = __import__(_name)
    except ModuleNotFoundError as e:
        if e.name != _name:
            raise
        continue
    SPEC.update(_mod.SPEC)
