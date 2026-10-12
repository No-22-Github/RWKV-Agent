# DISTILL-CANARY-fffc836c : distillation case
import json
case = json.load(open("case.json"))
LINES = {'data/a/x.bin': 1, 'data/b/y.bin': 1, 'data/c/z.bin': 1}
for _p, _n in LINES.items():
    assert len(case["files"][_p].splitlines()) == _n, _p
assert case["files"] == {"data/a/x.bin": "x\n", "data/b/y.bin": "y\n", "data/c/z.bin": "z\n"}
print(json.dumps({"expected_contains_any": ["sort -rh", "sort -hr", "sort -h", "sort -nr", "sort -rn", "sort -r"]}, ensure_ascii=False))
