# DISTILL-CANARY-2c0e7abb : distillation case
import json
import re

DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
case = json.load(open("case.json"))
prompt = case["turns"][0]["prompt"]
base = next(i for i, d in enumerate(DAYS) if d in prompt)
shift = int(re.search(r"(\d+) days later", prompt).group(1))
idx = (base + shift) % 7
assert idx == 3
assert case["files"]["README.md"].splitlines()[0].startswith("# Loomwork front-desk rota")
print(json.dumps({"expected_contains_any": [DAYS[idx], DAYS[idx][:3]]}))
