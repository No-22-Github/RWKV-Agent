# DISTILL-CANARY-ff713df2 : distillation case
import json
case = json.load(open("case.json"))
LINES = {'conf/backup.ini': 8, 'conf/backup.ini.bak': 5}
for _p, _n in LINES.items():
    assert len(case["files"][_p].splitlines()) == _n, _p
NEEDLES = [["conf/backup.ini", "[retention]\nkeep_days = 14"], ["conf/backup.ini", "[retention_cold]\nkeep_days = 90"], ["conf/backup.ini.bak", "keep_days = 7"]]
for _p, _s in NEEDLES:
    assert _s in case["files"][_p], (_p, _s)
print(json.dumps({"expected_contains_any": ["14"]}, ensure_ascii=False))
