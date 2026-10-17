# DISTILL-CANARY-95ed6a30 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '0b8cbcf38a4332c6819e57e50d0f10ece0ec73dd7005d0d72b7ef5cf48ef27b1', "fixture changed"
files = case["files"]
def compute(files):
    rows = []
    for l in files["README.md"].split("\n"):
        if l.startswith("- `GW_"):
            name = l.split("`")[1]
            default = l.split("`")[3]
            rows.append("| %s | %s |" % (name, default))
    return {"env-vars.md": "| Name | Default |\n|---|---|\n" + "\n".join(rows) + "\n"}

FINAL = compute(dict(files))
for path, rule in case["expect"]["files"].items():
    if "equals" in rule:
        assert FINAL[path] == rule["equals"], path
    elif "contains" in rule:
        assert all(s in FINAL[path] for s in rule["contains"]), path
print(json.dumps({"files": {k: v for k, v in FINAL.items() if k in case["expect"]["files"] and "unchanged" not in case["expect"]["files"][k]}}, ensure_ascii=False))
