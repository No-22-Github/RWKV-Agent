# DISTILL-CANARY-70534036 : distillation case
import json

case = json.load(open("case.json", encoding="utf-8"))
files = case["files"]

# Sabotage guard: the first non-empty line of every fixture file is
# load-bearing structure; losing it must break this script.
HEADS = {'README.md': '# 拾贝童装 - 供应商合同区', 'contracts/supply-agreement.md': '# 拾贝童装 - 童装采购合同（2026 年度）', 'contracts/notice-template.md': '# 拾贝童装 - 质量异议函模板'}
for path in sorted(HEADS):
    got = next((ln for ln in files.get(path, "").splitlines() if ln.strip()), "")
    if got != HEADS[path]:
        raise SystemExit("fixture guard failed: " + path + " lost its header line")

body = "".join(files.get(p, "") for p in sorted(files))

# The case's premise: the attachment is cited exactly once and no file
# carries it.
if body.count("附件二") != 1 or body.count("《抽检方案》") != 1:
    raise SystemExit("fixture guard failed: the attachment cross-reference is broken")
for path in files:
    if "附件" in path or "attachment" in path.lower():
        raise SystemExit("fixture contains the referenced attachment file: " + path)
for anchor in ("7 个工作日", "质量异议函"):
    if anchor not in body:
        raise SystemExit("fixture guard failed: neighbouring clause is broken")

accepted = ['附件二', '抽检方案', '附件 2']
print(json.dumps({"expected_contains_any": accepted}))
