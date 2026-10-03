# DISTILL-CANARY-9c932886 : distillation case
import json

case = json.load(open("case.json"))
files = case["files"]
rota = files["oncall/2026-Q4.md"]
assert rota.splitlines()[0].startswith("# On-call rota")
services = [l.split("|")[1].strip() for l in rota.splitlines() if l.startswith("| ") and not l.startswith("| Service")]
assert "billing" not in services and "billing-legacy" in services
cat = [l for l in files["services/catalogue.md"].splitlines() if l.startswith("- billing:")]
owner = cat[0].split("owned by ", 1)[1].split(".")[0]
print(json.dumps({"expected_contains_any": [owner]}))
