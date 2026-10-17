# DISTILL-CANARY-bf106c12 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '95736422aec634bf709d8bccb7600d900afa0ab95e480dc3694dd71fd4aafdea', "fixture changed"
def compute(files, web):
    t = files["资产/软件清单.csv"].replace("Quill DB,5.x,罗敏,2026-12-31", "Quill DB,5.x,罗敏,2027-03-31")
    return {"资产/软件清单.csv": t}, [["2027-03-31"]]

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
