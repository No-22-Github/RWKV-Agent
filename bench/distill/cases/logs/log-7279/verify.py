# DISTILL-CANARY-a26566ce : distillation case
import json
case = json.load(open("case.json"))
lines = [l for l in case["files"]["logs/nightly-2026-09-13.log"].splitlines() if l.strip()]
if not lines[0].startswith("# wellstone-ci nightly run 2026-09-13"):
    raise SystemExit("fixture guard failed: nightly log header is broken")

if any("FLAKY_RETRY_EXHAUSTED" in l for l in lines):
    raise SystemExit("fixture records FLAKY_RETRY_EXHAUSTED; the absent-event case is broken")
warns = [l for l in lines if "WARN  FLAKY_RETRY " in l]
if len(warns) != 2:
    raise SystemExit("fixture guard failed: FLAKY_RETRY decoy lines are broken")

accepted = ["FLAKY_RETRY_EXHAUSTED", "retry exhausted", "retries exhausted"]
print(json.dumps({"expected_contains_any": accepted}))
