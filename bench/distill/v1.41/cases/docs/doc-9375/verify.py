# DISTILL-CANARY-67304e80 : distillation case
import json
case = json.load(open("case.json"))
LINES = {'notes/纪要-1008.md': 8, 'notes/纪要-1001.md': 5}
for _p, _n in LINES.items():
    assert len(case["files"][_p].splitlines()) == _n, _p
NEEDLES = [["notes/纪要-1008.md", "数据迁移：周岚负责"], ["notes/纪要-1008.md", "迁移回滚演练：陈默负责"], ["notes/纪要-1001.md", "数据迁移：吴越负责"]]
for _p, _s in NEEDLES:
    assert _s in case["files"][_p], (_p, _s)
print(json.dumps({"expected_contains_any": ["周岚"]}, ensure_ascii=False))
