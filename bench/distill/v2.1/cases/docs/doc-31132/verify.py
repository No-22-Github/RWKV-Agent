# DISTILL-CANARY-1835c22b : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'a02301f436c7b0e6ccceaaae6d7a830da660df813018257a1f6511d16c557c18', "fixture changed"
def compute(files):
    out = "BEGIN\n"
    out = ""
    for l in files["通讯/contacts.txt"].strip().split("\n"):
        n, p = l.split(",")
        out += "BEGIN:VCARD\nFN:%s\nTEL:%s\nEND:VCARD\n" % (n, p)
    return {"通讯/contacts.vcf": out}

FINAL = compute(dict(case["files"]))
for path, rule in case["expect"]["files"].items():
    if "equals" in rule:
        assert FINAL[path] == rule["equals"], path
    elif "contains" in rule:
        assert all(s in FINAL[path] for s in rule["contains"]), path
    elif rule.get("unchanged"):
        assert path in case["files"] and path not in FINAL, path
print(json.dumps({"files": {k: v for k, v in FINAL.items() if k in case["expect"]["files"]}}, ensure_ascii=False))
