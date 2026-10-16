# DISTILL-CANARY-05525d72 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'e2ecfdf4a8e719fa835d0b83fd7c02405f4c64cbc6275640a1c798f26451abc9', "fixture changed"
def compute(files):
    rows = [l[2:].split(" / ") for l in files["成员/组.md"].split("\n") if l.startswith("- ")]
    out = "| Name | Role |\n|---|---|\n" + "".join("| %s | %s |\n" % tuple(r) for r in rows if r[1] != "前端")
    return {"成员/表.md": out}

FINAL = compute(dict(case["files"]))
for path, rule in case["expect"]["files"].items():
    if "equals" in rule:
        assert FINAL[path] == rule["equals"], path
    elif "contains" in rule:
        assert all(s in FINAL[path] for s in rule["contains"]), path
    elif rule.get("unchanged"):
        assert path in case["files"] and path not in FINAL, path
print(json.dumps({"files": {k: v for k, v in FINAL.items() if k in case["expect"]["files"]}}, ensure_ascii=False))
