# DISTILL-CANARY-46da8c10 : distillation case
import json

case = json.load(open("case.json", encoding="utf-8"))
files = case["files"]

# Sabotage guard: the first non-empty line of every fixture file is
# load-bearing structure; losing it must break this script.
HEADS = {'README.md': '# 观澜印务 - 对外报价归档', 'pricing/price-list-2026-03.md': '# 观澜印务 - 对外价目表（2026 年 3 月版）', 'pricing/matrix-notes.md': '# 报价备注'}
for path in sorted(HEADS):
    got = next((ln for ln in files.get(path, "").splitlines() if ln.strip()), "")
    if got != HEADS[path]:
        raise SystemExit("fixture guard failed: " + path + " lost its header line")

body = "".join(files.get(p, "") for p in sorted(files))

MISSING = "9 月"
if MISSING in body:
    raise SystemExit("fixture contains a September edition; the absent-edition case is broken")
for anchor in ("2026 年 3 月版", "0.86"):
    if anchor not in body:
        raise SystemExit("fixture guard failed: neighbouring edition is broken")

accepted = ['9 月版', '9月版', '2026 年 9 月']
print(json.dumps({"expected_contains_any": accepted}))
