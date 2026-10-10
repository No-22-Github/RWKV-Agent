# DISTILL-CANARY-122fc8a1 : distillation case
import json

case = json.load(open("case.json", encoding="utf-8"))
files = case["files"]

# Sabotage guard: the first non-empty line of every fixture file is
# load-bearing structure; losing it must break this script.
HEADS = {'README.md': '# 云汀文旅 - 退款改签政策库', 'policy/index.txt': 'refund.md｜退款规则', 'policy/refund.md': '# 云汀文旅 - 退款规则（2026 年 6 月修订）', 'policy/reschedule.md': '# 云汀文旅 - 改签规则（2026 年 6 月修订）'}
for path in sorted(HEADS):
    got = next((ln for ln in files.get(path, "").splitlines() if ln.strip()), "")
    if got != HEADS[path]:
        raise SystemExit("fixture guard failed: " + path + " lost its header line")

body = "".join(files.get(p, "") for p in sorted(files))

MISSING = "台风"
if MISSING in body:
    raise SystemExit("fixture defines a typhoon clause; the absent-clause case is broken")
for anchor in ("暴雨橙色预警", "暴雪预警", "20 元"):
    if anchor not in body:
        raise SystemExit("fixture guard failed: neighbouring clause " + anchor + " is broken")

accepted = ['台风红色预警', '台风预警', '台风']
print(json.dumps({"expected_contains_any": accepted}))
