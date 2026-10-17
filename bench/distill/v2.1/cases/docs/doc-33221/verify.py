# DISTILL-CANARY-d50eef7e : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '6c91149c838fb35ee15c0f23197583026d9cac0e40bcc4e0a1e17e6a7cd457a9', "fixture changed"
files = case["files"]
def compute(files):
    ver, rows = "", []
    for l in files["CHANGELOG.md"].split("\n"):
        if l.startswith("## "):
            ver = l[3:]
        elif "BREAKING:" in l:
            rows.append("| %s | %s |" % (ver, l.split("BREAKING:")[1].strip()))
    return {"breaking.md": "| Version | Change |\n|---|---|\n" + "\n".join(rows) + "\n"}

FINAL = compute(dict(files))
for path, rule in case["expect"]["files"].items():
    if "equals" in rule:
        assert FINAL[path] == rule["equals"], path
    elif "contains" in rule:
        assert all(s in FINAL[path] for s in rule["contains"]), path
print(json.dumps({"files": {k: v for k, v in FINAL.items() if k in case["expect"]["files"] and "unchanged" not in case["expect"]["files"][k]}}, ensure_ascii=False))
