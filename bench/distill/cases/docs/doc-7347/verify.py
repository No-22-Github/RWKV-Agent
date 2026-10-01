# DISTILL-CANARY-3177504a : distillation case
import json

case = json.load(open("case.json", encoding="utf-8"))
files = case["files"]

# Sabotage guard: the first non-empty line of every fixture file is
# load-bearing structure; losing it must break this script.
HEADS = {'README.md': '# 蒹葭农场 - 质检文件归档', 'standards/qc-standard-v2.md': '# 蒹葭农场 - 稻谷质检标准（v2，2024 年 6 月版）', 'standards/sampling-plan.md': '# 蒹葭农场 - 抽样方案'}
for path in sorted(HEADS):
    got = next((ln for ln in files.get(path, "").splitlines() if ln.strip()), "")
    if got != HEADS[path]:
        raise SystemExit("fixture guard failed: " + path + " lost its header line")

body = "".join(files.get(p, "") for p in sorted(files))

MISSING = "v3"
if MISSING in body:
    raise SystemExit("fixture contains v3; the absent-version case is broken")
if "qc-standard-v3.md" in case["files"]:
    raise SystemExit("fixture contains qc-standard-v3.md; the absent-version case is broken")
for anchor in ("13.5%", "抽样方案"):
    if anchor not in body:
        raise SystemExit("fixture guard failed: neighbouring file is broken")

accepted = ['质检标准 v3', '质检标准v3', 'v3']
print(json.dumps({"expected_contains_any": accepted}))
