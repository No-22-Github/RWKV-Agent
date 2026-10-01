# DISTILL-CANARY-47c56ce7 : distillation case
import json

case = json.load(open("case.json", encoding="utf-8"))
files = case["files"]

# Sabotage guard: the first non-empty line of every fixture file is
# load-bearing structure; losing it must break this script.
HEADS = {'README.md': '# 白石诊所 - 就诊指南库', 'guide/index.txt': 'visit-flow.md｜第一章 就诊流程', 'guide/visit-flow.md': '# 白石诊所 - 就诊流程（第一章）', 'guide/fees.md': '# 白石诊所 - 收费说明（第三章）'}
for path in sorted(HEADS):
    got = next((ln for ln in files.get(path, "").splitlines() if ln.strip()), "")
    if got != HEADS[path]:
        raise SystemExit("fixture guard failed: " + path + " lost its header line")

body = "".join(files.get(p, "") for p in sorted(files))

# The case's premise: the referenced chapter is cited exactly once and no
# file carries it.
REF = "《医保报销指引》"
if body.count(REF) != 1 or body.count("第五章") != 1 or body.count("起付线") != 1:
    raise SystemExit("fixture guard failed: the chapter cross-reference is broken")
for path in files:
    if "医保" in path:
        raise SystemExit("fixture contains the referenced chapter file: " + path)
for anchor in ("挂号费 10 元", "自费项目"):
    if anchor not in body:
        raise SystemExit("fixture guard failed: neighbouring section is broken")

accepted = ['医保报销指引', '第五章', '医保报销']
print(json.dumps({"expected_contains_any": accepted}))
