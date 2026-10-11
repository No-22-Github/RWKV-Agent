# DISTILL-CANARY-4eec19f5 : distillation case
import json
case = json.load(open("case.json"))
assert case["files"]["configs/README.md"].startswith("# Configs")
def parse(path):
    out = {}
    for row in case["files"][path].splitlines():
        if row.startswith("#") or "=" not in row:
            continue
        key, value = row.split("=", 1)
        out[key.strip()] = value.strip()
    return out
bad = []
for name in ("app", "cache", "log"):
    staging = parse("configs/staging/" + name + ".conf")
    prod = parse("configs/prod/" + name + ".conf")
    assert staging.keys() == prod.keys(), name
    for key in staging:
        if key.endswith("_host") or key.endswith("_url"):
            continue
        if staging[key] != prod[key]:
            bad.append(key)
assert len(bad) == 1, bad
print(json.dumps({"expected_string": bad[0]}))
