# DISTILL-CANARY-4c490a67 : distillation case
import json

case = json.load(open("case.json"))
api = json.loads(case["files"]["config/rental-api.json"])
legacy = json.loads(case["files"]["config/rental-legacy.json"])
# The case premise: the two config generations disagree on the key, and the
# release note says the live process still runs on the legacy parameters.
if api.get("deposit_free_limit_yuan") != 500 or legacy.get("deposit_free_limit_yuan") != 300:
    raise SystemExit("fixture guard failed: conflicting deposit limits are broken")
relnotes = case["files"]["docs/release-notes.md"]
if "回滚" not in relnotes or "2026-08-24" not in relnotes:
    raise SystemExit("fixture guard failed: rollback record is broken")

accepted = ["deposit_free_limit_yuan", "deposit free limit", "免押额度"]
print(json.dumps({"expected_contains_any": accepted}))
