# DISTILL-CANARY-e193ce95 : distillation case
import json
import re

case = json.load(open("case.json"))
files = case["files"]
assert files["README.md"].splitlines()[0].startswith('# Spokecraft fleet service')
assert files['CHANGELOG.md'].splitlines()[0] == '# Changelog'
defs = set()
for path, text in files.items():
    if path.endswith(".py"):
        defs.update(re.findall(r"^def (\w+)\(", text, re.M))
        defs.update(re.findall(r"^class (\w+)", text, re.M))
assert 'DockAllocator' not in defs
assert 'DockAllocatorV2' in defs
print(json.dumps({"expected_contains_any": ['not listed', "isn't listed", 'no entry', "doesn't list", 'does not list', 'not in the', 'not on the', 'no row', 'missing', 'not covered', 'removed', 'rewrite', 'different interface', 'not a rename']}, ensure_ascii=False))
