# DISTILL-CANARY-a6b79a65 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '31e3acd9b1aa36e41fc13af13d63f48e0a5a8c895a99fd5634511599b9f9f7b9', "fixture changed"
def compute(files):
    d = {}
    for l in files["logs/access.log"].strip().split("\n"):
        ip, _, _, code = l.split()
        if code.startswith("5"):
            d[ip] = d.get(ip, 0) + 1
    return {"logs/5xx_by_ip.txt": "".join("%s %d\n" % (k, d[k]) for k in sorted(d, key=lambda k: (-d[k], k)))}

FINAL = compute(dict(case["files"]))
for path, rule in case["expect"]["files"].items():
    if "equals" in rule:
        assert FINAL[path] == rule["equals"], path
    elif "contains" in rule:
        assert all(s in FINAL[path] for s in rule["contains"]), path
    elif rule.get("unchanged"):
        assert path in case["files"] and path not in FINAL, path
print(json.dumps({"files": {k: v for k, v in FINAL.items() if k in case["expect"]["files"]}}, ensure_ascii=False))
