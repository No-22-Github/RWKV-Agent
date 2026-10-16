# DISTILL-CANARY-70f9ed4d : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '4cd960f81daa8447194c1e4938f861a035c4540ca92317d774eafdceb9956e6a', "fixture changed"
def compute(files):
    rows = [l.split(",") for l in files["账号/users.csv"].strip().split("\n")[1:]]
    rows = [r for r in rows if r[2] != "guest"]
    return {"账号/active.csv": "id,name,role\n" + "".join("%s,%s,%s\n" % (r[0], r[1].upper(), r[2]) for r in rows)}

FINAL = compute(dict(case["files"]))
for path, rule in case["expect"]["files"].items():
    if "equals" in rule:
        assert FINAL[path] == rule["equals"], path
    elif "contains" in rule:
        assert all(s in FINAL[path] for s in rule["contains"]), path
    elif rule.get("unchanged"):
        assert path in case["files"] and path not in FINAL, path
print(json.dumps({"files": {k: v for k, v in FINAL.items() if k in case["expect"]["files"]}}, ensure_ascii=False))
