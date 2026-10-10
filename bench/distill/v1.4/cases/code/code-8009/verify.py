# DISTILL-CANARY-1d498fd3 : distillation case
import json
import re

case = json.load(open("case.json"))
files = case["files"]
assert files["README.md"].splitlines()[0].startswith('# Glidepool rental core')
assert files['CHANGELOG.md'].splitlines()[0] == '# Changelog'
defs = set()
for path, text in files.items():
    if path.endswith(".py"):
        defs.update(re.findall(r"^def (\w+)\(", text, re.M))
        defs.update(re.findall(r"^class (\w+)", text, re.M))
assert 'compute_rental_credit' not in defs
assert 'apply_rental_credit' in defs
print(json.dumps({"expected_contains_any": ['not listed', "isn't listed", 'no entry', "doesn't list", 'does not list', 'not in the', 'not on the', 'no row', 'missing', 'not covered', 'deleted', 'wallet', 'moved', 'no rounding']}, ensure_ascii=False))
