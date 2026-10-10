#!/usr/bin/env python3
"""Every number in reports/b10b.md (see tools/batch_stats.py). Run from the repo root."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
from batch_stats import stats  # noqa: E402
from common import SHELVED  # noqa: E402

SUB = {'m7a': [('web', 8036, 8063), ('hyb', 8021, 8032)], 'm7b': [('web', 8064, 8091), ('hyb', 8033, 8044)], 'm8a': [('nt', 8046, 8065), ('tab', 8058, 8067), ('cfg', 8054, 8063), ('doc', 8041, 8050)]}
stats("b10b", SUB, SHELVED)
