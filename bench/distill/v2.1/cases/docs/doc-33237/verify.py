# DISTILL-CANARY-f6655096 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'ba601603c42af792ff788491df35bc9c7be2593581313331cc9df8e3ad26a369', "fixture changed"
files = case["files"]
def compute(files):
    rows = [l for l in files["refs/links.txt"].strip().split("\n") if " - https://" in l]
    return {"refs/https-only.md": "".join("- [%s](%s)\n" % tuple(l.split(" - ")) for l in rows)}

FINAL = compute(dict(files))
for path, rule in case["expect"]["files"].items():
    if "equals" in rule:
        assert FINAL[path] == rule["equals"], path
    elif "contains" in rule:
        assert all(s in FINAL[path] for s in rule["contains"]), path
print(json.dumps({"files": {k: v for k, v in FINAL.items() if k in case["expect"]["files"] and "unchanged" not in case["expect"]["files"][k]}}, ensure_ascii=False))
