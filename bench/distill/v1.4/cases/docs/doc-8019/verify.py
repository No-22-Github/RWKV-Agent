# DISTILL-CANARY-5b09074b : distillation case
import json

case = json.load(open("case.json"))
files = case["files"]
assert files["README.md"].splitlines()[0].startswith("Par-level handbook")
hb = files["handbook/par-handbook.md"].splitlines()
sects = [l for l in hb if l.startswith("## ")]
assert "## 3 Duvet covers" not in sects and "awaits the floor supervisors" in "\n".join(hb)
assert any("Par is 5" in l for l in hb)
tracker = files["handbook/floor-count-tracker.md"]
assert "awaiting data entry" in tracker
words = ["pending", "awaits", "awaiting", "not set", "no number", "carries no", "no duvet"]
print(json.dumps({"expected_contains_any": words}))
