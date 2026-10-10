"""Where things live under bench/distill (layout: bench/distill/README.md).

Every distill tool resolves repo paths through here, so a layout change
touches this file only.
"""
import glob
import json
import os

TOOLS = os.path.dirname(os.path.abspath(__file__))
DISTILL = os.path.dirname(TOOLS)
REPO = os.path.dirname(os.path.dirname(DISTILL))
COMMON = os.path.join(DISTILL, "common")
EXCLUDE_JSONL = os.path.join(COMMON, "exclude.jsonl")


def version_dir(version, *parts):
    """bench/distill/<version>/<parts...>, e.g. version_dir("v1.4", "b09_work")."""
    return os.path.join(DISTILL, version, *parts)


def cases_dir(version):
    return version_dir(version, "cases")


def teacher_script(version, batch):
    """A teacher action script, e.g. teacher_script("v1.3", "b05-baseline")."""
    return version_dir(version, "teacher", batch + ".jsonl")


def case_files():
    """Every live case.json across versions (shelved cases excluded), sorted."""
    return sorted(glob.glob(os.path.join(DISTILL, "v*", "cases", "*", "*", "case.json")))


def find_case_dir(case_id):
    hits = glob.glob(os.path.join(DISTILL, "v*", "cases", "*", case_id))
    return hits[0] if len(hits) == 1 else None


def find_case(case_id):
    d = find_case_dir(case_id)
    if d is None or not os.path.exists(os.path.join(d, "case.json")):
        return None
    with open(os.path.join(d, "case.json")) as f:
        return json.load(f)
