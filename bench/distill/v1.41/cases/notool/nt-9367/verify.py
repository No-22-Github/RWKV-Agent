# DISTILL-CANARY-94746f1e : distillation case
import json
case = json.load(open("case.json"))
LINES = {'名单/报名表.txt': 8}
for _p, _n in LINES.items():
    assert len(case["files"][_p].splitlines()) == _n, _p
assert case["files"] == {"名单/报名表.txt": "王芳\n李强\n张敏\n王芳\n赵磊\n李强\n王芳\n孙悦\n"}
print(json.dumps({"expected_contains_any": ["uniq -d", "uniq -D", "awk"]}, ensure_ascii=False))
