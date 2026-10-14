# DISTILL-CANARY-4ed1f490 : distillation case
import json

case = json.load(open("case.json", encoding="utf-8"))
files = case["files"]

# Sabotage guard: the first non-empty line of every fixture file is
# load-bearing structure; losing it must break this script.
HEADS = {'README.md': '# 兰台律所 - 员工手册库', 'handbook/index.txt': 'expenses.md｜第五章 差旅与报销', 'handbook/expenses.md': '# 兰台律所 - 差旅与报销（第五章）', 'handbook/procedure.md': '# 兰台律所 - 立案流程（第六章）'}
for path in sorted(HEADS):
    got = next((ln for ln in files.get(path, "").splitlines() if ln.strip()), "")
    if got != HEADS[path]:
        raise SystemExit("fixture guard failed: " + path + " lost its header line")

body = "".join(files.get(p, "") for p in sorted(files))

# The case's premise: the referenced chapter is cited exactly once and no
# file carries it.
REF = "《对外文件签章规范》"
if body.count(REF) != 1 or body.count("第九章") != 1:
    raise SystemExit("fixture guard failed: the chapter cross-reference is broken")
for path in files:
    if "签章" in path:
        raise SystemExit("fixture contains the referenced chapter file: " + path)
for anchor in ("600 元", "利益冲突"):
    if anchor not in body:
        raise SystemExit("fixture guard failed: neighbouring chapter is broken")

accepted = ['对外文件签章', '第九章', '签章规范']
print(json.dumps({"expected_contains_any": accepted}))
