# DISTILL-CANARY-c9ae3594 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '50191f53529933ee1fef2cc41b9b2e53912ae969345200716c45e434c5de11ba', "fixture changed"
def compute(files):
    rows = []
    for p in sorted(files):
        d = dict(l.split(": ") for l in files[p].strip().split("\n"))
        rows.append((d["name"], d["port"], d["replicas"]))
    return {"服务/清单.csv": "服务,端口,副本数\n" + "".join("%s,%s,%s\n" % r for r in rows)}

FINAL = compute(dict(case["files"]))
for path, rule in case["expect"]["files"].items():
    if "equals" in rule:
        assert FINAL[path] == rule["equals"], path
    elif "contains" in rule:
        assert all(s in FINAL[path] for s in rule["contains"]), path
    elif rule.get("unchanged"):
        assert path in case["files"] and path not in FINAL, path
print(json.dumps({"files": {k: v for k, v in FINAL.items() if k in case["expect"]["files"]}}, ensure_ascii=False))
