# DISTILL-CANARY-eedb1f58 : distillation case
LINES = {'日志/2026-10-05.log': 278, '日志/2026-10-06.log': 353, '日志/2026-10-07.log': 322}

import json
case = json.load(open("case.json"))
pl = case["files"]["脚本/failcount.pl"]
assert "$c[1] eq 'FAIL' && $c[2] eq 'sync'" in pl
n = 0
for path, text in case["files"].items():
    if not path.endswith(".log"):
        continue
    assert len(text.splitlines()) == LINES[path], path
    for row in text.splitlines():
        parts = row.split(" ")
        assert len(parts) == 4, row
        n += parts[1] == "FAIL" and parts[2] == "sync"
print(json.dumps({"expected_contains_any": [str(n)]}))
