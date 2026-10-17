# DISTILL-CANARY-1d72c5d8 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'db2afeaa21302e8801a7f44f30a08d914616b7ac550539e9c499d7cf3b7a0471', "fixture changed"
def compute(files, web):
    import re
    a = re.search(r"Pro: \$(\d+) per month", web[0]["content"]).group(1)
    b = re.search(r"\$(\d+) per year", web[1]["content"]).group(1)
    return {}, [[a], [b]]

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
