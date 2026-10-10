# DISTILL-CANARY-4b286685 : distillation case
import json
import re

case = json.load(open("case.json"))
files = case["files"]
assert files["README.md"].splitlines()[0].startswith('# Cyclelet dock map')
assert files['docs/migration.md'].splitlines()[0] == '# Migration notes'
defs = set()
for path, text in files.items():
    if path.endswith(".py"):
        defs.update(re.findall(r"^def (\w+)\(", text, re.M))
        defs.update(re.findall(r"^class (\w+)", text, re.M))
assert 'resolve_dock_zone' not in defs
assert 'resolve_zone_fee' in defs
print(json.dumps({"expected_contains_any": ['not listed', "isn't listed", 'no entry', "doesn't list", 'does not list', 'not in the', 'not on the', 'no row', 'missing', 'not covered', 'removed', 'permit platform', 'unrelated', 'moved']}, ensure_ascii=False))
