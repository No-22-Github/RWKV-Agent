# DISTILL-CANARY-0df50c36 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '0581d6724746c1441999a5d1dd783448576d96d130c8d16c63a7052c64db6dc9', "fixture changed"
def compute(files):
    d = {}
    for w in files["词表/words.txt"].strip().split("\n"):
        d[w] = d.get(w, 0) + 1
    return {"词表/频次.txt": "".join("%s\t%d\n" % (k, d[k]) for k in sorted(d, key=lambda k: (-d[k], k)))}

FINAL = compute(dict(case["files"]))
for path, rule in case["expect"]["files"].items():
    if "equals" in rule:
        assert FINAL[path] == rule["equals"], path
    elif "contains" in rule:
        assert all(s in FINAL[path] for s in rule["contains"]), path
    elif rule.get("unchanged"):
        assert path in case["files"] and path not in FINAL, path
print(json.dumps({"files": {k: v for k, v in FINAL.items() if k in case["expect"]["files"]}}, ensure_ascii=False))
