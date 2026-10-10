# DISTILL-CANARY-0aa64902 : distillation case
import json

case = json.load(open("case.json", encoding="utf-8"))
files = case["files"]

# Sabotage guard: the first non-empty line of every fixture file is
# load-bearing structure; losing it must break this script.
HEADS = {'README.md': '# 栖梧书院 - 行政制度库', 'docs/index.txt': 'conduct.md｜员工行为规范', 'docs/conduct.md': '# 栖梧书院 - 员工行为规范（2026 年 3 月修订）', 'docs/leave.md': '# 栖梧书院 - 考勤与请假制度（2026 年 3 月修订）'}
for path in sorted(HEADS):
    got = next((ln for ln in files.get(path, "").splitlines() if ln.strip()), "")
    if got != HEADS[path]:
        raise SystemExit("fixture guard failed: " + path + " lost its header line")

body = "".join(files.get(p, "") for p in sorted(files))

MISSING = "学历造假"
if MISSING in body:
    raise SystemExit("fixture defines " + MISSING + "; the absent-clause case is broken")
for anchor in ("代打卡", "记大过一次", "病假"):
    if anchor not in body:
        raise SystemExit("fixture guard failed: neighbouring clause " + anchor + " is broken")

accepted = ['学历造假', '学历 造假', '造假学历']
print(json.dumps({"expected_contains_any": accepted}))
