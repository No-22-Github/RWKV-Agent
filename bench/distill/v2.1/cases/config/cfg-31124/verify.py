# DISTILL-CANARY-bca7ac09 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'e1a5d9880ab55ba5c033e348460faaf8d74c37e0558af4bf6934b75d98fb91f9', "fixture changed"
def compute(files):
    out = "[servers]\n"
    for l in files["配置/servers.txt"].strip().split("\n"):
        n, ip, p = l.split()
        out += "%s ansible_host=%s ansible_port=%s\n" % (n, ip, p)
    return {"配置/inventory.ini": out}

FINAL = compute(dict(case["files"]))
for path, rule in case["expect"]["files"].items():
    if "equals" in rule:
        assert FINAL[path] == rule["equals"], path
    elif "contains" in rule:
        assert all(s in FINAL[path] for s in rule["contains"]), path
    elif rule.get("unchanged"):
        assert path in case["files"] and path not in FINAL, path
print(json.dumps({"files": {k: v for k, v in FINAL.items() if k in case["expect"]["files"]}}, ensure_ascii=False))
