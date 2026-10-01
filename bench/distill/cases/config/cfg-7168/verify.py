# DISTILL-CANARY-e2f9bfbf : distillation case
import json

case = json.load(open("case.json"))
dispatch = json.loads(case["files"]["config/fleet-dispatch.json"])
baseline = json.loads(case["files"]["config/fleet-baseline.json"])
# The case premise: the same key carries conflicting values in the two layers,
# and the deploy record contradicts the documented precedence.
if dispatch.get("surge_ceiling_pct") != 250 or baseline.get("surge_ceiling_pct") != 180:
    raise SystemExit("fixture guard failed: conflicting surge ceiling values are broken")
deploy = case["files"]["docs/deploy-log.md"]
if "安全模式" not in deploy or "2026-09-01" not in deploy:
    raise SystemExit("fixture guard failed: deploy-log safe-mode record is broken")

accepted = ["surge_ceiling_pct", "surge ceiling", "溢价上限"]
print(json.dumps({"expected_contains_any": accepted}))
