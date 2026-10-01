# DISTILL-CANARY-c10fe58b : distillation case
import json

case = json.load(open("case.json"))
lines = case["files"]["logs/egress-2026-07-21.jsonl"].splitlines()
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

flush_events = [r for r in events if r.get("kind") == "egress_flush"]
if len(flush_events) < 2:
    raise SystemExit("fixture guard failed: flush events missing")
seen = {}
for r in flush_events:
    seen.setdefault(r["event_id"], r["bytes_out"])
if len(flush_events) <= len(seen):
    raise SystemExit("fixture guard failed: re-sent events missing")
probes = sum(1 for r in events if r.get("kind") == "egress_probe")
if probes < 1:
    raise SystemExit("fixture guard failed: probe events missing")
value = sum(seen.values())
print(json.dumps({"expected_number": value}))
