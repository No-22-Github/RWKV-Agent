# DISTILL-CANARY-e27a9d31 : distillation case
"""Recompute the current Marlbeck ledger revision from the revisions page."""
import json
import re

case = json.load(open("case.json"))
page = case["web_fixture"][0]["content"]
rows = re.findall(r"\| (\d+) \| marlbeck-writer ([\d.]+) \| ([^|]+?) \|", page)
current = [int(revision) for revision, _writer, note in rows if note.startswith("current")]
older = [int(revision) for revision, _writer, note in rows if not note.startswith("current")]
if len(current) != 1 or len(older) < 2:
    raise SystemExit("the revision table must mark one current revision and two older ones")
if max(older) >= current[0]:
    raise SystemExit("the current revision must be the newest one")
print(json.dumps({"expected_number": current[0]}))
