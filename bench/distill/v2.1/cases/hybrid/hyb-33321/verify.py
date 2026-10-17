# DISTILL-CANARY-c247e7e4 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '3e98e70b655c3a2bdd5916d8aec49115480a33168c15930ea445e4fa65b566fd', "fixture changed"
def compute(files, web):
    slow = []
    for l in files["监控/latency.log"].splitlines():
        p = l.split()
        ms = int(p[3][:-2])
        slow.append((ms, p[2]))
    n = sum(1 for m, _ in slow if m > 800)
    worst = max(slow)[1]
    return {"监控/慢请求.txt": "数量=%d\n最慢接口=%s\n" % (n, worst)}, [[str(n), worst]]

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
