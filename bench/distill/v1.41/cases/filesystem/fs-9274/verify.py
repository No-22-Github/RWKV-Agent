# DISTILL-CANARY-7a88a574 : distillation case
import json
case = json.load(open("case.json"))
assert sum(len(t.splitlines()) for t in case["files"].values()) == 113
assert case["files"]['incoming/README.md'].startswith('# Incoming')
assert 'hold-*.txt are on hold' in case["files"]['incoming/README.md']
FINAL = json.loads(r'''{"done/report-01.txt": "report 1 line 0\nreport 1 line 1\nreport 1 line 2\nreport 1 line 3\nreport 1 line 4\nreport 1 line 5\nreport 1 line 6\nreport 1 line 7\n", "done/report-02.txt": "report 2 line 0\nreport 2 line 1\nreport 2 line 2\n", "done/report-03.txt": "report 3 line 0\nreport 3 line 1\nreport 3 line 2\nreport 3 line 3\nreport 3 line 4\nreport 3 line 5\nreport 3 line 6\nreport 3 line 7\n", "done/report-04.txt": "report 4 line 0\nreport 4 line 1\nreport 4 line 2\nreport 4 line 3\nreport 4 line 4\nreport 4 line 5\n", "done/report-05.txt": "report 5 line 0\nreport 5 line 1\nreport 5 line 2\nreport 5 line 3\nreport 5 line 4\nreport 5 line 5\nreport 5 line 6\nreport 5 line 7\n", "done/report-06.txt": "report 6 line 0\nreport 6 line 1\nreport 6 line 2\nreport 6 line 3\nreport 6 line 4\nreport 6 line 5\nreport 6 line 6\nreport 6 line 7\n", "done/report-07.txt": "report 7 line 0\nreport 7 line 1\nreport 7 line 2\nreport 7 line 3\nreport 7 line 4\nreport 7 line 5\nreport 7 line 6\nreport 7 line 7\nreport 7 line 8\n", "done/report-08.txt": "report 8 line 0\nreport 8 line 1\nreport 8 line 2\nreport 8 line 3\nreport 8 line 4\nreport 8 line 5\nreport 8 line 6\n"}''')
for path, text in FINAL.items():
    assert case["expect"]["files"][path]["equals"] == text, path
for path, rule in {"incoming/hold-01.txt": 1, "incoming/hold-02.txt": 1, "incoming/hold-03.txt": 1, "done/old-01.txt": 1, "done/old-02.txt": 1, "done/old-03.txt": 1, "done/old-04.txt": 1, "done/old-05.txt": 1, "incoming/README.md": 1}.items():
    assert case["expect"]["files"][path] == {"unchanged": True}, path
state = dict(case["files"])
state.update(FINAL)
n = sum(len(t.splitlines()) for p, t in state.items() if p.startswith("done/"))
assert n == 99, n
print(json.dumps({"expected_number": n}))
