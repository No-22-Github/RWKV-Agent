# DISTILL-CANARY-85d5ac07 : distillation case
import json
case = json.load(open("case.json"))
LINES = {'stats/2026-05.txt': 56, 'stats/2026-06.txt': 62, 'stats/2026-07.txt': 68, 'stats/2026-08.txt': 59, 'stats/2026-09.txt': 64, 'stats/2026-10.txt': 77, 'stats/README.md': 4, 'release/NEXT.md': 4, 'release/NEXT.md.bak': 4}
for _p, _n in LINES.items():
    assert len(case["files"][_p].splitlines()) == _n, _p
assert case["files"]["stats/README.md"].startswith("# Download stats")
assert case["files"]["release/NEXT.md"].splitlines()[2] == "codename: Harbor"
assert case["files"]["release/NEXT.md.bak"].splitlines()[2] == "codename: Lantern"
n = 0
for path, text in case["files"].items():
    if path.startswith("stats/2026-") and path.endswith(".txt"):
        for r in text.splitlines():
            p, v = r.split(" ")
            n += int(v) * (p == "linux")
print(json.dumps({"expected_contains_any": [str(n)] + (["{:,}".format(n)] if n >= 1000 else [])}))
