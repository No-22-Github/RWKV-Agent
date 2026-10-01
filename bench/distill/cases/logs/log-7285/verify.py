# DISTILL-CANARY-95f75000 : distillation case
import json
case = json.load(open("case.json"))

records = [json.loads(l) for l in case["files"]["logs/sluice-2026-09a.jsonl"].splitlines() if l.strip()]
# Positive control: the log opens with its start-of-day record, so the
# whole window below is covered by the recomputation.
if records[0].get("event") != "collector_start":
    raise SystemExit("fixture guard failed: log does not open with collector_start")

# The case premise: the volume ends on 12 September and the only alarm
# in it belongs to an earlier day.
if records[-1].get("event") != "archive_stop" or not records[-1]["ts"].startswith("2026-09-12"):
    raise SystemExit("fixture guard failed: volume end record is broken")
if any(r["ts"] >= "2026-09-13" for r in records):
    raise SystemExit("fixture covers 13 September; the outside-window case is broken")
alarms = [r for r in records if r.get("event") == "GATE_ALARM"]
if len(alarms) != 1 or not alarms[0]["ts"].startswith("2026-09-10T02:14"):
    raise SystemExit("fixture guard failed: 10 September alarm decoy is broken")

accepted = ["GATE_ALARM", "gate alarm", "闸门异常"]
print(json.dumps({"expected_contains_any": accepted}))
