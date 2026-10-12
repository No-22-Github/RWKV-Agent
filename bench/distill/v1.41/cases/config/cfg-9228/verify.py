# DISTILL-CANARY-12f645a7 : distillation case
import json
case = json.load(open("case.json"))
LINES = {'门店/价目表.txt': 5, '门店/价目表-去年.txt': 5}
for _p, _n in LINES.items():
    assert len(case["files"][_p].splitlines()) == _n, _p
for path, idx, row in [["门店/价目表.txt", 2, "拿铁 26 元"], ["门店/价目表-去年.txt", 2, "拿铁 22 元"]]:
    assert case["files"][path].splitlines()[idx] == row, (path, idx)
print(json.dumps({"expected_contains_any": ["26"]}, ensure_ascii=False))
