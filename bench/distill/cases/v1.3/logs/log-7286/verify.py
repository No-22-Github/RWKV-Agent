# DISTILL-CANARY-7abe1543 : distillation case
import json
case = json.load(open("case.json"))
lines = [l for l in case["files"]["logs/dock-scans-2026-09-08-10.log"].splitlines() if l.strip()]
if not lines[0].startswith("# ellersmuir-depot dock scan log"):
    raise SystemExit("fixture guard failed: volume header is broken")

# The case premise: the volume ends on 10 September.
if not any("dock-scans-2026-09-11-14" in l for l in lines):
    raise SystemExit("fixture guard failed: rollover note is broken")
scans = [l for l in lines if " SCAN " in l]
if any(l[:13] >= "2026-09-11T" for l in scans):
    raise SystemExit("fixture covers 11 September; the outside-window case is broken")
lates = [l for l in scans if "DOCK_LATE" in l]
if len(lates) != 2:
    raise SystemExit("fixture guard failed: DOCK_LATE decoy lines are broken")

accepted = ["DOCK_LATE", "dock late"]
print(json.dumps({"expected_contains_any": accepted}))
