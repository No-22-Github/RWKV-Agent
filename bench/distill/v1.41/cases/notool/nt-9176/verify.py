# DISTILL-CANARY-57738857 : distillation case
import json
case = json.load(open("case.json"))
LINES = {'app/config/web.yml': 2, 'app/config/worker.yml': 2, 'app/config/cron.yml': 2}
for _p, _n in LINES.items():
    assert len(case["files"][_p].splitlines()) == _n, _p
assert case["files"] == {"app/config/web.yml": "env: staging\nname: web\n", "app/config/worker.yml": "env: staging\nname: worker\n", "app/config/cron.yml": "env: staging\nname: cron\n"}
print(json.dumps({"expected_contains_any": ["sed -i", "sed "]}, ensure_ascii=False))
