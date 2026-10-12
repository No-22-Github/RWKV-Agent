# DISTILL-CANARY-505e9407 : distillation case
import json
case = json.load(open("case.json"))
LINES = {'notes/week-1.txt': 88, 'notes/week-2.txt': 79, 'notes/week-3.txt': 64, 'notes/week-4.txt': 65, 'notes/week-5.txt': 76, 'notes/week-6.txt': 67, 'notes/README.md': 4, 'team/RULES.md': 4, 'team/RULES.md.bak': 4}
for _p, _n in LINES.items():
    assert len(case["files"][_p].splitlines()) == _n, _p
assert case["files"]["notes/README.md"].startswith("# Notes")
assert case["files"]["team/RULES.md"].splitlines()[2] == "- Merging requires 2 approvals."
assert case["files"]["team/RULES.md.bak"].splitlines()[2] == "- Merging requires 1 approval."
n = 0
for path, text in case["files"].items():
    if path.startswith("notes/week-") and path.endswith(".txt"):
        for r in text.splitlines():
            assert r.startswith("["), r
            n += r.startswith("[TODO] ")
print(json.dumps({"expected_number": n}))
