#!/usr/bin/env python3
"""Every number in reports/b10d.md (see tools/batch_stats.py). Run from the repo root."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
from batch_stats import stats  # noqa: E402
from common import SHELVED  # noqa: E402

SUB = {'m6a': [('tab', 8400, 8439)], 'm6b': [('log', 8400, 8429)], 'm6c': [('tab', 8440, 8489)],
       'm6d': [('tab', 8490, 8519), ('log', 8430, 8444), ('code', 8400, 8414)]}
stats("b10d", SUB, SHELVED)
