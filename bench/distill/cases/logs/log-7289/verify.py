# DISTILL-CANARY-0ff43e0e : distillation case
import json
case = json.load(open("case.json"))
lines = [l for l in case["files"]["logs/feed-dock-2026-09-11.log"].splitlines() if l.strip()]
if not lines[0].startswith("# ottergate-stables feed dock log barn=main opened 2026-09-11T04:55"):
    raise SystemExit("fixture guard failed: log header is broken")

# The case premise: five sensor lines are cut mid-write over the 06:00-06:55
# block, and no readable DOCK_SCAN exists anywhere.
corrupt = [l for l in lines if "\x7f" in l]
if len(corrupt) != 5:
    raise SystemExit("fixture guard failed: corrupted sensor block is broken")
if any("DOCK_SCAN" in l for l in lines):
    raise SystemExit("fixture records a readable DOCK_SCAN; the corrupted-window case is broken")
if not any("05:58:36" in l for l in lines):
    raise SystemExit("fixture guard failed: pre-corruption records are broken")

accepted = ["DOCK_SCAN", "dock scan"]
print(json.dumps({"expected_contains_any": accepted}))
