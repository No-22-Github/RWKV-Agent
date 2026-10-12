# DISTILL-CANARY-8cc1de4b : distillation case
import json
case = json.load(open("case.json"))
LINES = {'审计/events-0912.jsonl': 430, '审计/events-0913.jsonl': 427, '审计/events-0914.jsonl': 389, '审计/说明.md': 4}
for _p, _n in LINES.items():
    assert len(case["files"][_p].splitlines()) == _n, _p
assert case["files"]["审计/说明.md"].startswith("# 审计日志说明")
users = set()
files = 0
for path, text in case["files"].items():
    if not path.endswith(".jsonl"):
        continue
    files += 1
    for row in text.splitlines():
        e = json.loads(row)
        assert sorted(e) == ["action", "ok", "ts", "user"], row
        if e["action"] == "login" and e["ok"] is False:
            users.add(e["user"])
assert files == 3
print(json.dumps({"expected_number": len(users)}))
