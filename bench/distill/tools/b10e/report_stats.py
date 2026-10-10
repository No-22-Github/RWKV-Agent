#!/usr/bin/env python3
"""Every number in reports/b10e.md (see tools/batch_stats.py). Run from the repo root."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
from batch_stats import stats  # noqa: E402
from common import SHELVED  # noqa: E402

SUB = {'m5a': [('cfg', 8600, 8649)], 'm5b': [('cfg', 8650, 8664), ('doc', 8600, 8614)],
       'm5c': [('cfg', 8665, 8684), ('code', 8600, 8609), ('hyb', 8600, 8609)],
       'm5d': [('doc', 8615, 8644), ('cfg', 8685, 8714)], 'm5e': [('scr', 8001, 8030)]}
stats("b10e", SUB, SHELVED)
