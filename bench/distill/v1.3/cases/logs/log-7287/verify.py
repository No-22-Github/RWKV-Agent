# DISTILL-CANARY-8d59dd39 : distillation case
import json
case = json.load(open("case.json"))

records = [json.loads(l) for l in case["files"]["logs/gates-2026-09-05.jsonl"].splitlines() if l.strip()]
# Positive control: the log opens with its start-of-day record, so the
# whole window below is covered by the recomputation.
if records[0].get("event") != "collector_start":
    raise SystemExit("fixture guard failed: log does not open with collector_start")

# The case premise: the workspace only holds the 5 September export.
if not all(r["ts"].startswith("2026-09-05") for r in records):
    raise SystemExit("fixture covers another day; the outside-window case is broken")
offs = [r for r in records if r.get("event") == "GATE_OFFLINE"]
if len(offs) != 2 or "B3" not in offs[0]["detail"] or "B7" not in offs[1]["detail"]:
    raise SystemExit("fixture guard failed: 5 September offline decoys are broken")

accepted = ["GATE_OFFLINE", "gate offline", "闸机离线"]
print(json.dumps({"expected_contains_any": accepted}))
