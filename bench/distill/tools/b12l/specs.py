"""Behavior specs for the b12l cases, merged into ../b12/behavior.py SPEC.
Each module keeps its own SPEC dict beside its builders; modules are loaded by file path so they do not clash
with the same-named modules of other batches."""
import importlib.util
import os

SPEC = {}
_here = os.path.dirname(os.path.abspath(__file__))
for _name in ("m9", "m10"):
    _path = os.path.join(_here, _name + ".py")
    if not os.path.exists(_path):
        continue
    _spec = importlib.util.spec_from_file_location("b12l_" + _name, _path)
    _mod = importlib.util.module_from_spec(_spec)
    import sys
    sys.path.insert(0, _here)
    try:
        _spec.loader.exec_module(_mod)
    finally:
        sys.path.remove(_here)
    SPEC.update(_mod.SPEC)
