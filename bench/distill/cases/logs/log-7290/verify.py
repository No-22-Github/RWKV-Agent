# DISTILL-CANARY-34ef867f : distillation case
import json
case = json.load(open("case.json"))
lines = [l for l in case["files"]["logs/paddle-gear-2026-09.log"].splitlines() if l.strip()]
if not lines[0].startswith("# tetchley-canal paddle gear log vol.9 opened 2026-09-01"):
    raise SystemExit("fixture guard failed: volume header is broken")

# The case premise: five repeated-fragment lines overwrite the 9-11 September
# block, and no readable PADDLE_JAM exists anywhere.
fragments = [l for l in lines if l.startswith("paddle gear check ok paddle gear che")]
if len(fragments) != 5:
    raise SystemExit("fixture guard failed: overwritten fragment block is broken")
if any("PADDLE_JAM" in l for l in lines):
    raise SystemExit("fixture records PADDLE_JAM; the corrupted-window case is broken")
checks = [l for l in lines if l[:4] == "2026" and " paddle gear ok" in l]
if len(checks) != 5:
    raise SystemExit("fixture guard failed: dated CHECK records are broken")

accepted = ["PADDLE_JAM", "paddle jam"]
print(json.dumps({"expected_contains_any": accepted}))
