# DISTILL-CANARY-96f4d7fd : distillation case
import json

case = json.load(open("case.json", encoding="utf-8"))
files = case["files"]

# Sabotage guard: the first non-empty line of every fixture file is
# load-bearing structure; losing it must break this script.
HEADS = {'README.md': '# 漱玉民宿 - 服务标准库', 'standards/index.txt': 'housekeeping.md｜客房查房标准', 'standards/housekeeping.md': '# 漱玉民宿 - 客房查房标准（2026 年 5 月修订）', 'standards/amenities.md': '# 漱玉民宿 - 客房备品标准（2026 年 5 月修订）'}
for path in sorted(HEADS):
    got = next((ln for ln in files.get(path, "").splitlines() if ln.strip()), "")
    if got != HEADS[path]:
        raise SystemExit("fixture guard failed: " + path + " lost its header line")

body = "".join(files.get(p, "") for p in sorted(files))

MISSING = "加床"
if MISSING in body:
    raise SystemExit("fixture defines an extra-bed fee; the partial-answer case is broken")
# Half the answer is verifiable and pinned in the housekeeping standard.
if "30 分钟" not in files.get("standards/housekeeping.md", ""):
    raise SystemExit("fixture guard failed: the inspection window rule is broken")
# Positive control: the near-neighbour deposit wording the decoy comes from.
if "200 元" not in body:
    raise SystemExit("fixture guard failed: the deposit clause is broken")

accepted = ['加床费', '加床']
print(json.dumps({"expected_contains_any": accepted}))
