# DISTILL-CANARY-555a8f0f : distillation case
import json
case = json.load(open("case.json"))
LINES = {'备份/说明.txt': 2}
for _p, _n in LINES.items():
    assert len(case["files"][_p].splitlines()) == _n, _p
assert case["files"] == {"备份/说明.txt": "backup-2026-10.tar.gz 由夜间任务生成。\n内容：conf/ 与 data/ 两个顶层目录。\n"}
print(json.dumps({"expected_contains_any": ["xzf", "zxf", "xvzf", "zxvf", "tar -x", "tar x", "--extract"]}, ensure_ascii=False))
