# DISTILL-CANARY-e3049b2d : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'f345180649ef1be92a5f47265de0f4fff7ecfa458ce6a3ad6b121dd972610b11', "fixture changed"
def compute(files):
    out = ""
    for l in files["env/prod.env"].strip().split("\n"):
        k, v = l.split("=", 1)
        out += "%s=%s\n" % (k, "***" if k in ("DB_PASS", "API_KEY") else v)
    return {"env/prod.sample.env": out}

FINAL = compute(dict(case["files"]))
for path, rule in case["expect"]["files"].items():
    if "equals" in rule:
        assert FINAL[path] == rule["equals"], path
    elif "contains" in rule:
        assert all(s in FINAL[path] for s in rule["contains"]), path
    elif rule.get("unchanged"):
        assert path in case["files"] and path not in FINAL, path
print(json.dumps({"files": {k: v for k, v in FINAL.items() if k in case["expect"]["files"]}}, ensure_ascii=False))
