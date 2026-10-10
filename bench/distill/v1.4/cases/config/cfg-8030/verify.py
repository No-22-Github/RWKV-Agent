# DISTILL-CANARY-5f80d90e : distillation case
import json

case = json.load(open("case.json"))
files = case["files"]
assert files["README.md"].startswith("Whitecrest Linen Services chemical dosing config")
doc = files["docs/dosing-config.md"].splitlines()
assert doc[0] == "# Dosing controller settings"
lib = [l for l in doc if l.startswith("- surfactant_holdoff_s:")][0].split("When unset, the ")[1].split(" ")[0]
for path in ("config/dosing.toml", "config/env/production.toml"):
    assert "surfactant_holdoff_s" not in files[path]
print(json.dumps({"expected_string": lib}))
