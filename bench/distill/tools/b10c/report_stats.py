#!/usr/bin/env python3
"""Every number in reports/b10c.md (see tools/batch_stats.py). Run from the repo root."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
from batch_stats import stats  # noqa: E402
from common import SHELVED  # noqa: E402

SUB = {'m4a': [('cfg', 8200, 8211), ('doc', 8200, 8211), ('fs', 8200, 8210), ('nt', 8200, 8234)], 'm4b': [('web', 8200, 8229)], 'm4c': [('log', 8200, 8219), ('tab', 8200, 8229)]}
stats("b10c", SUB, SHELVED)
