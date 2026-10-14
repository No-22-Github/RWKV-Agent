# DISTILL-CANARY-d661f7f7 : distillation case
import json
case = json.load(open("case.json"))
LINES = {'运维/备份策略.txt': 4, '运维/备份策略.txt.bak': 4}
for _p, _n in LINES.items():
    assert len(case["files"][_p].splitlines()) == _n, _p
for path, idx, row in [["运维/备份策略.txt", 2, "增量备份：每天 02:00，保留 14 份"], ["运维/备份策略.txt.bak", 2, "增量备份：每天 02:00，保留 7 份"]]:
    assert case["files"][path].splitlines()[idx] == row, (path, idx)
print(json.dumps({"expected_contains_any": ["14", "十四"]}, ensure_ascii=False))
