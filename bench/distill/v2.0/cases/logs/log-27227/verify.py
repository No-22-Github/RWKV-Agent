# DISTILL-CANARY-eed5dad6 : distillation case
import json

case = json.load(open("case.json"))
lines = case["files"]["logs/fangkuan-2026-06-18.jsonl"].splitlines()
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

holds = [r for r in events if r.get("amount_cny_hold", 0) > 0]
if len(holds) < 1:
    raise SystemExit("fixture guard failed: hold rows missing")
value = round(sum(r["amount_cny"] for r in events), 2)
print(json.dumps({"expected_number": value}))
