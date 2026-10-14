# DISTILL-CANARY-249d5457 : distillation case
import json

case = json.load(open("case.json", encoding="utf-8"))
files = case["files"]

# Sabotage guard: the first non-empty line of every fixture file is
# load-bearing structure; losing it must break this script.
HEADS = {'README.md': '# 沉璧物业 - 装修与园区规约库', 'estate/index.txt': 'renovation.md｜装修管理规定', 'estate/renovation.md': '# 沉璧物业 - 装修管理规定（2026 年 4 月修订）', 'estate/parking.md': '# 沉璧物业 - 车辆与地库管理（2026 年 4 月修订）'}
for path in sorted(HEADS):
    got = next((ln for ln in files.get(path, "").splitlines() if ln.strip()), "")
    if got != HEADS[path]:
        raise SystemExit("fixture guard failed: " + path + " lost its header line")

body = "".join(files.get(p, "") for p in sorted(files))

MISSING = "夜间"
if MISSING in body:
    raise SystemExit("fixture defines a night-works clause; the absent-clause case is broken")
for anchor in ("8:30–18:00", "电梯护板"):
    if anchor not in body:
        raise SystemExit("fixture guard failed: neighbouring clause " + anchor + " is broken")

accepted = ['夜间施工', '夜间 施工', '夜间许可']
print(json.dumps({"expected_contains_any": accepted}))
