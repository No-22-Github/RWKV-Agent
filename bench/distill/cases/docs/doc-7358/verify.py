# DISTILL-CANARY-8b5830f5 : distillation case
import json

case = json.load(open("case.json", encoding="utf-8"))
files = case["files"]

# Sabotage guard: the first non-empty line of every fixture file is
# load-bearing structure; losing it must break this script.
HEADS = {'README.md': '# 临渚测绘 - 外业作业规程库', 'spec/index.txt': 'uav-rules.md｜无人机作业规程', 'spec/uav-rules.md': '# 临渚测绘 - 无人机作业规程（2026 年 4 月修订）', 'spec/equipment-checklist.md': '# 临渚测绘 - 出队装备清单'}
for path in sorted(HEADS):
    got = next((ln for ln in files.get(path, "").splitlines() if ln.strip()), "")
    if got != HEADS[path]:
        raise SystemExit("fixture guard failed: " + path + " lost its header line")

body = "".join(files.get(p, "") for p in sorted(files))

MISSING = "备用电池"
if MISSING in body:
    raise SystemExit("fixture defines a spare battery limit; the partial-answer case is broken")
# Half the answer is verifiable and pinned in the flight rules.
if "1 个工作日" not in files.get("spec/uav-rules.md", ""):
    raise SystemExit("fixture guard failed: the flight declaration rule is broken")
# Positive control: the near-neighbour battery wording the decoy comes from.
if "6 块" not in body:
    raise SystemExit("fixture guard failed: the equipment checklist is broken")

accepted = ['备用电池', '电池上限', '电池携带']
print(json.dumps({"expected_contains_any": accepted}))
