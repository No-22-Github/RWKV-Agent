# DISTILL-CANARY-5a812e29 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '9940143c88e5b70e37b2f2be96ae1ab6c0d7f7d91509706146b28c4361192d2b', "fixture changed"
def compute(files, web):
    import re
    out = []
    for k in ("A", "B"):
        n = int(re.search(r"seats: (\d+)", files["it/team%s.txt" % k]).group(1))
        p = 14 if n <= 10 else (11 if n <= 50 else 9)
        out.append([str(n * p)])
    return {}, out

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
