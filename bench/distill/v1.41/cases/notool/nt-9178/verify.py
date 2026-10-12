# DISTILL-CANARY-c27068f1 : distillation case
import json
case = json.load(open("case.json"))
LINES = {'日志/app-2026-10-09.log': 1, '日志/app-2026-10-10.log': 1, '日志/app-2026-10-11.log': 1}
for _p, _n in LINES.items():
    assert len(case["files"][_p].splitlines()) == _n, _p
assert case["files"] == {"日志/app-2026-10-09.log": "2026-10-09 INFO started\n", "日志/app-2026-10-10.log": "2026-10-10 INFO started\n", "日志/app-2026-10-11.log": "2026-10-11 INFO started\n"}
print(json.dumps({"expected_contains_any": ["-mtime", "-mmin", "-newermt"]}, ensure_ascii=False))
