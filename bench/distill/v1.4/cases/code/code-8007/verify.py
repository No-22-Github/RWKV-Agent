# DISTILL-CANARY-27b018c3 : distillation case
import json
import re

case = json.load(open("case.json"))
files = case["files"]
assert files["README.md"].splitlines()[0].startswith('# Voltway battery library')
assert files['docs/scoring.md'].splitlines()[0] == '# Scoring'
defs = set()
for path, text in files.items():
    if path.endswith(".py"):
        defs.update(re.findall(r"^def (\w+)\(", text, re.M))
        defs.update(re.findall(r"^class (\w+)", text, re.M))
assert 'pack_health_score' not in defs
assert 'pack_health_index' in defs
print(json.dumps({"expected_contains_any": ['not listed', "isn't listed", 'no entry', "doesn't list", 'does not list', 'not in the', 'not on the', 'no row', 'missing', 'not covered', 'removed', 'telemetry', 'approximation', 'not the same']}, ensure_ascii=False))
