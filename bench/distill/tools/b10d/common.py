"""b10d (v1.4 M3) settings; the writer itself is ../casegen.py."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from casegen import Batch  # noqa: E402

_batch = Batch(salt="b10d", author="llm:claude-sonnet-5-5-b10d", version="v1.4")

# S5 triage: 0/3 cases where the teacher, not the criteria, was wrong in all
# three runs. They are written as usual and then moved to cases-shelved, so a
# rebuild reproduces the same live set. Reasons are in reports/b10d.md.
SHELVED = {}


def write_case(cid, **kw):
    _batch.write_case(cid, **kw)
    if cid in SHELVED:
        import shutil
        live = os.path.join(_batch.cases, _scen(cid), cid)
        shelf = os.path.join(os.path.dirname(_batch.cases), "cases-shelved", _scen(cid), cid)
        if os.path.isdir(shelf):
            shutil.rmtree(shelf)
        os.makedirs(os.path.dirname(shelf), exist_ok=True)
        shutil.move(live, shelf)


def _scen(cid):
    from casegen import SCEN
    return SCEN[cid.split("-")[0]]


def revised(changes):
    """write_case that bumps the listed cases to version 2 and records why in a
    NOTES Changelog section (S5 triage of the teacher runs: criteria fixes and
    case bugs). changes maps case id -> one-line changelog entry."""
    def wrapped(cid, **kw):
        if cid in changes:
            kw["version"] = 2
            entry = "## Changelog\n- v2：%s\n\n" % changes[cid]
            notes = kw["notes"]
            mark = "## Why the answer is unique"
            kw["notes"] = notes.replace(mark, entry + mark, 1) if mark in notes else notes.rstrip("\n") + "\n\n" + entry
        return write_case(cid, **kw)
    return wrapped
