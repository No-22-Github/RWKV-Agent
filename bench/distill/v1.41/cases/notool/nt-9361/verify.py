# DISTILL-CANARY-009b01a7 : distillation case
import json
case = json.load(open("case.json"))
LINES = {'项目/src/main.py': 1, '项目/docs/README.md': 1, '项目/notes/todo.txt': 1}
for _p, _n in LINES.items():
    assert len(case["files"][_p].splitlines()) == _n, _p
assert case["files"] == {"项目/src/main.py": "print('hi')\n", "项目/docs/README.md": "# 项目说明\n", "项目/notes/todo.txt": "整理目录\n"}
print(json.dumps({"expected_contains_any": ["-empty"]}, ensure_ascii=False))
