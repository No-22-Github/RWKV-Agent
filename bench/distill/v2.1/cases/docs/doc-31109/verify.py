# DISTILL-CANARY-370649dc : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '0645ace42c2920a3fba4b071ad1f7c69ea85c114a1692bb732ef5510772857a4', "fixture changed"
def compute(files):
    rows = [[x.strip() for x in l.split("|")] for l in files["notes/books.txt"].strip().split("\n")]
    rows.sort(key=lambda r: (int(r[1]), r[0]))
    return {"notes/books.md": "| Title | Year | Author |\n|---|---|---|\n" + "".join("| %s | %s | %s |\n" % tuple(r) for r in rows)}

FINAL = compute(dict(case["files"]))
for path, rule in case["expect"]["files"].items():
    if "equals" in rule:
        assert FINAL[path] == rule["equals"], path
    elif "contains" in rule:
        assert all(s in FINAL[path] for s in rule["contains"]), path
    elif rule.get("unchanged"):
        assert path in case["files"] and path not in FINAL, path
print(json.dumps({"files": {k: v for k, v in FINAL.items() if k in case["expect"]["files"]}}, ensure_ascii=False))
