# DISTILL-CANARY-c95b04f2 : distillation case
import json

case = json.load(open("case.json"))
files = case["files"]
def parse(text):
    out = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or "=" not in line:
            continue
        key, _, value = line.partition("=")
        out[key.strip()] = value.strip()
    return out
prod = parse(files["envs/prod.env"])
staging = parse(files["envs/staging.env"])
facts = []
for key in sorted(prod):
    if key in staging and staging[key] != prod[key]:
        facts.append(prod[key])
print(json.dumps({"expected_contains_any": facts}))
