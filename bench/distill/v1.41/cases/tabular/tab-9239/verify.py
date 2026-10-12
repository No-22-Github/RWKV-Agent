# DISTILL-CANARY-7d45f858 : distillation case
import json
case = json.load(open("case.json"))
LINES = {'作业/第1周.txt': 55, '作业/第2周.txt': 74, '作业/第3周.txt': 70, '作业/第4周.txt': 73, '作业/第5周.txt': 74, '作业/第6周.txt': 65, '作业/说明.md': 4, '课程表.md': 6, '课程表-上学期.md': 6}
for _p, _n in LINES.items():
    assert len(case["files"][_p].splitlines()) == _n, _p
assert case["files"]["作业/说明.md"].startswith("# 作业记录说明")
assert case["files"]["课程表.md"].splitlines()[4] == "周三 第二节：线性代数"
assert case["files"]["课程表-上学期.md"].splitlines()[4] == "周三 第二节：高等数学"
n = 0
for path, text in case["files"].items():
    if path.startswith("作业/第") and path.endswith(".txt"):
        for r in text.splitlines():
            sid, name, s = r.split(" ")
            n += s == "缺交"
print(json.dumps({"expected_contains_any": ["线性代数"] + [str(n)] + (["{:,}".format(n)] if n >= 1000 else [])}, ensure_ascii=False))
