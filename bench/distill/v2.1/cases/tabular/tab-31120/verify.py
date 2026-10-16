# DISTILL-CANARY-79b531de : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '09ec67cfc17361e00f57af788a5c979b325a6513b4755b965dabd00a13db1d71', "fixture changed"
def compute(files):
    out = []
    for l in files["库/借阅.csv"].strip().split("\n")[1:]:
        r, b, o, back = l.split(",")
        if not back:
            out.append("%s,%s,%s" % (b, r, o))
    return {"库/未还.csv": "书名,读者,借出\n" + "".join(x + "\n" for x in sorted(out))}

FINAL = compute(dict(case["files"]))
for path, rule in case["expect"]["files"].items():
    if "equals" in rule:
        assert FINAL[path] == rule["equals"], path
    elif "contains" in rule:
        assert all(s in FINAL[path] for s in rule["contains"]), path
    elif rule.get("unchanged"):
        assert path in case["files"] and path not in FINAL, path
print(json.dumps({"files": {k: v for k, v in FINAL.items() if k in case["expect"]["files"]}}, ensure_ascii=False))
