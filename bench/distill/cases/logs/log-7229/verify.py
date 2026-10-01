# DISTILL-CANARY-388e8386 : distillation case
import json

case = json.load(open("case.json"))
lines = case["files"]["logs/bench-2026-02-11.jsonl"].splitlines()
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

checkpoints = [r for r in records if r.get("record") == "checkpoint"]
if len(checkpoints) != 1 or checkpoints[0].get("bus_error_sensors_dropped_total") == None:
    raise SystemExit("fixture guard failed: checkpoint record malformed")
value = sum(r.get("sensors_dropped", 0) for r in events if r.get("kind") == "bus_error")
if checkpoints[0]["bus_error_sensors_dropped_total"] == value:
    raise SystemExit("fixture guard failed: checkpoint total equals the true sum")
other_kinds = [r for r in events if r.get("kind") == "bus_error" and False]
zero_events = [r for r in events if r.get("kind") == "bus_error" and r.get("sensors_dropped", 0) == 0]
if zero_events:
    raise SystemExit("fixture guard failed: zero-valued bus_error rows present")
value
print(json.dumps({"expected_number": value}))
