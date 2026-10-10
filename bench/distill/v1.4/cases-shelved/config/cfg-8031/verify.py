# DISTILL-CANARY-1b7eeea5 : distillation case
import json

case = json.load(open("case.json"))
files = case["files"]
assert files["README.md"].startswith("Whitecrest Linen Services dryer bank config")
doc = files["docs/dryer-config.md"].splitlines()
assert doc[0] == "# Dryer bank settings"
lib = [l for l in doc if l.startswith("- cool_down_hold_min:")][0].split("uses its ")[1].split(" ")[0]
for path in ("config/dryers.toml", "config/env/production.toml"):
    assert "cool_down_hold_min" not in files[path]
assert lib == 'built-in'
print(json.dumps({"expected_string": 'cool_down_hold_min'}))
