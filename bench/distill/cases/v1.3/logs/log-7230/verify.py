# DISTILL-CANARY-63a9b913 : distillation case
import json

case = json.load(open("case.json"))
lines = case["files"]["logs/huidiao-2026-05-25.jsonl"].splitlines()
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

summaries = [r for r in records if r.get("record") == "checkpoint-summary"]
if len(summaries) != 1:
    raise SystemExit("fixture guard failed: 日终汇总记录应恰好一条")
raw = 0
seen = {}
for r in events:
    if r.get("status") == "success":
        raw += 1
        seen.setdefault(r["callback_id"], r["fee_cny"])
if raw <= len(seen):
    raise SystemExit("fixture guard failed: 重发记录缺失")
if round(summaries[0].get("fee_total_cny", -1), 2) == round(sum(seen.values()), 2):
    raise SystemExit("fixture guard failed: 汇总草稿值等于真值")
value = round(sum(seen.values()), 2)
print(json.dumps({"expected_number": value}))
