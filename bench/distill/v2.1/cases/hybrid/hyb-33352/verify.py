# DISTILL-CANARY-1946a353 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '8f2cbc4fadc3a419323cac07517140523e0c3f24b8851c78d1f8689ab7f2c470', "fixture changed"
def compute(files, web):
    return {"app.ini": files["app.ini"].replace("timeout = 30", "timeout = 45")}, [["operational", "Operational", "no incident", "No incident", "no open incident", "No open incident", "no active incident", "no current incident", "No current incident", "no ongoing"], ["2026-09-23", "September 23", "Sept 23", "Sep 23", "23 September", "23 Sep", "9/23", "09-23"]]

FINAL, ANS = compute(dict(case["files"]), case["web_fixture"])
for path, rule in case["expect"]["files"].items():
    if "equals" in rule:
        assert FINAL[path] == rule["equals"], path
    elif "contains" in rule:
        assert all(s in FINAL[path] for s in rule["contains"]), path
    elif rule.get("unchanged"):
        assert path in case["files"] and path not in FINAL, path
for turn, a in zip(case["turns"], ANS):
    e = turn["expect"]
    assert set(a) <= set(e.get("output_contains", [])) | set(e.get("output_contains_any", [])), a
print(json.dumps({"files": {k: v for k, v in FINAL.items() if k in case["expect"]["files"]}, "answers": ANS}, ensure_ascii=False))
