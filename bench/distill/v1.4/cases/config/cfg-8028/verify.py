# DISTILL-CANARY-b48cb604 : distillation case
import json

case = json.load(open("case.json"))
files = case["files"]
assert files["README.md"].startswith("Whitecrest Linen Services plant config")
doc = files["docs/tunnel-config.md"].splitlines()
assert doc[0] == "# Tunnel 2 settings"
lib = [l for l in doc if l.startswith("- extract_ramp_s:")][0].split("built into its ")[1].split(" ")[0]
for path in ("config/tunnel-2.toml", "config/env/production.toml"):
    assert "extract_ramp_s" not in files[path]
print(json.dumps({"expected_string": lib}))
