# DISTILL-CANARY-c125cea6 : distillation case
import json

case = json.load(open("case.json"))
lines = case["files"]["logs/nav-2026-08-09.jsonl"].splitlines()
records = [json.loads(line) for line in lines]

meta = records[0]
if meta.get("record") != "journal-meta" :
    raise SystemExit("fixture guard failed: first line must be the journal-meta record")
close = records[-1]
if close.get("record") != "journal-close":
    raise SystemExit("fixture guard failed: last line must be the journal-close record")
events = [r for r in records if r.get("record") == "event"]
if meta.get("event_lines") != len(events) or close.get("event_lines") != len(events):
    raise SystemExit("fixture guard failed: event count does not match meta/close records")

raw = 0
seen = set()
say = 0
warns = 0
for r in events:
    if r.get("component") == "nav-fuse" and r.get("level") == "ERROR":
        raw += 1
        seen.add(r["event_id"])
    if r.get("level") == "ERROR" and r.get("component") != "nav-fuse" and "nav-fuse" in r.get("detail", ""):
        say += 1
    if r.get("level") == "WARN" and r.get("component") == "nav-fuse":
        warns += 1
if raw <= len(seen) or say < 1 or warns < 1:
    raise SystemExit("fixture guard failed: decoys or re-sends missing")
value = len(seen)
print(json.dumps({"expected_number": value}))
