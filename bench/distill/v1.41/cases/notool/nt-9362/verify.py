# DISTILL-CANARY-a06d9c52 : distillation case
import json
case = json.load(open("case.json"))
LINES = {'src/a.c': 2, 'src/b.c': 1, 'src/util/c.c': 2}
for _p, _n in LINES.items():
    assert len(case["files"][_p].splitlines()) == _n, _p
assert case["files"] == {"src/a.c": "// SPDX-License-Identifier: MIT\nint a(void){return 1;}\n", "src/b.c": "int b(void){return 2;}\n", "src/util/c.c": "// SPDX-License-Identifier: MIT\nint c(void){return 3;}\n"}
print(json.dumps({"expected_contains_any": ["-L", "--files-without-match"]}, ensure_ascii=False))
