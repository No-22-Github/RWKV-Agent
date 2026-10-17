# DISTILL-CANARY-14ad0808 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'ae89ccee0645714592b480a1e1a05150ecefd9891033d406d2aa329c6ca2fb9c', "fixture changed"
files = case["files"]
def compute(files):
    rows = []
    for l in files["员工/生日.txt"].strip().split("\n"):
        n, d = l.split(" ")
        m, day = d.split("月")
        if m == "10":
            rows.append((int(day.rstrip("日")), n, d))
    rows.sort()
    return {"员工/十月寿星.md": "".join("- %s：%s\n" % (n, d) for _, n, d in rows)}

FINAL = compute(dict(files))
for path, rule in case["expect"]["files"].items():
    if "equals" in rule:
        assert FINAL[path] == rule["equals"], path
    elif "contains" in rule:
        assert all(s in FINAL[path] for s in rule["contains"]), path
print(json.dumps({"files": {k: v for k, v in FINAL.items() if k in case["expect"]["files"] and "unchanged" not in case["expect"]["files"][k]}}, ensure_ascii=False))
