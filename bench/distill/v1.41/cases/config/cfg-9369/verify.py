# DISTILL-CANARY-4769784a : distillation case
import json
case = json.load(open("case.json"))
LINES = {'deploy/limits.toml': 12, 'deploy/limits.toml.old': 5}
for _p, _n in LINES.items():
    assert len(case["files"][_p].splitlines()) == _n, _p
NEEDLES = [["deploy/limits.toml", "[worker]\nmemory_mb = 768"], ["deploy/limits.toml", "[worker-canary]\nmemory_mb = 512"], ["deploy/limits.toml.old", "memory_mb = 256"]]
for _p, _s in NEEDLES:
    assert _s in case["files"][_p], (_p, _s)
print(json.dumps({"expected_contains_any": ["768"]}, ensure_ascii=False))
