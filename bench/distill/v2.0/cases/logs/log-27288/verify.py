# DISTILL-CANARY-b02b1dd4 : distillation case
import json
case = json.load(open("case.json"))
lines = [l for l in case["files"]["logs/temp-alarm-2026-09.jsonl"].splitlines() if l.strip()]
parsed = []
corrupt = 0
for l in lines:
    try:
        parsed.append(json.loads(l))
    except ValueError:
        corrupt += 1

# Positive control: the log opens with its start record, and the duty note
# anchors the disk-full incident.
if parsed[0].get("event") != "collector_start":
    raise SystemExit("fixture guard failed: log does not open with collector_start")
if corrupt != 6:
    raise SystemExit("fixture guard failed: half-written block is broken")
if not any("-16.8C" in r.get("detail", "") for r in parsed):
    raise SystemExit("fixture guard failed: post-recovery records are broken")
duty = case["files"]["docs/duty-notes.md"]
if "磁盘写满" not in duty:
    raise SystemExit("fixture guard failed: duty note is broken")

# The case premise: no HIGH_TEMP_ALARM survives in the parseable records.
if any(r.get("event") == "HIGH_TEMP_ALARM" for r in parsed):
    raise SystemExit("fixture records HIGH_TEMP_ALARM; the corrupted-window case is broken")

accepted = ["HIGH_TEMP_ALARM", "high temp alarm", "高温告警"]
print(json.dumps({"expected_contains_any": accepted}))
