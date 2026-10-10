# DISTILL-CANARY-b2a6c995 : distillation case
import json

case = json.load(open("case.json"))
files = case["files"]
assert files["README.md"].startswith("Whitecrest Linen Services flatwork line config")
doc = files["docs/ironer-config.md"].splitlines()
assert doc[0] == "# Flatwork ironer settings"
lib = [l for l in doc if l.startswith("- dwell_adjust_pct:")][0].split("falls back to its ")[1].split(" ")[0]
for path in ("config/ironer-1.toml", "config/env/production.toml"):
    assert "dwell_adjust_pct" not in files[path]
assert lib == 'on-board'
print(json.dumps({"expected_string": 'dwell_adjust_pct'}))
