# DISTILL-CANARY-af3634b0 : distillation case
import json

case = json.load(open("case.json"))
files = case["files"]
# sabotage guard: bank verify deletes the first non-empty line of this file first
assert files["logs/order-sync-2026-10-11.log"].splitlines()[0] == "Reeftide Pet Supply - online order sync log, 2026-10-11"

log = files["logs/order-sync-2026-10-11.log"].splitlines()
# The scheduled sync run was skipped; the only imports are staff manual batches.
assert any("sync job skipped" in l for l in log)
manual = [l for l in log if " MANUAL " in l]
assert len(manual) == 2 and all("(staff" in l for l in manual)
runbook = files["ops/SYNC-RUNBOOK.md"]
assert "paused" in runbook and "not sync runs" in runbook
words = ["paused", "migration", "manual", "no run", "did not run", "didn't run", "skipped", "no sync run", "no import", "staff"]
print(json.dumps({"expected_contains_any": words}, ensure_ascii=False))
