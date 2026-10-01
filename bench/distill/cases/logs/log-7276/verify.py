# DISTILL-CANARY-85e41e17 : distillation case
import json
case = json.load(open("case.json"))

records = [json.loads(l) for l in case["files"]["logs/live-class-2026-09-15.jsonl"].splitlines() if l.strip()]
# Positive control: the log opens with its start-of-day record, so the
# whole window below is covered by the recomputation.
if records[0].get("event") != "service_start":
    raise SystemExit("fixture guard failed: log does not open with service_start")

# The case premise: the stall event is nowhere in the day log, while the
# decoy event the careless count quotes is present.
if any(r.get("event") == "STREAM_STALL" for r in records):
    raise SystemExit("fixture records STREAM_STALL; the absent-event case is broken")
lags = [r for r in records if r.get("event") == "STREAM_LAG_WARN"]
if len(lags) != 3:
    raise SystemExit("fixture guard failed: STREAM_LAG_WARN decoy records are broken")

accepted = ["STREAM_STALL", "STREAM STALL", "stream_stall"]
print(json.dumps({"expected_contains_any": accepted}))
