# DISTILL-CANARY-8f3e5d1f : distillation case
import json

case = json.load(open("case.json"))
files = case["files"]
# sabotage guard: bank verify deletes the first non-empty line of this file first
assert files["logs/kalk-dosing-2026-10-09.log"].splitlines()[0] == "Tidepool Corner - dosing pump event log, 2026-10-09"

log = files["logs/kalk-dosing-2026-10-09.log"].splitlines()
warns = [l for l in log if " WARN " in l]
assert warns and all("KD-2 spare" in l for l in warns)
assert len(warns) == 3
assert any("removed for impeller rebuild" in l for l in log)
ledger = files["maintenance/PUMP-LEDGER.md"]
assert "rebuild 2026-10-09" in ledger and "reinstalled 2026-10-10" in ledger
words = ["rebuild", "removed", "out of service", "didn't run", "did not run", "logged nothing", "no events", "no entries", "not in service", "offline", "reinstalled", "no warnings"]
print(json.dumps({"expected_contains_any": words}, ensure_ascii=False))
