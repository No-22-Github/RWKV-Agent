# DISTILL-CANARY-dab56c04 : distillation case
import json

case = json.load(open("case.json"))
files = case["files"]
old = sorted(p for p in files if p.startswith("体测报告/旧供应商归档/") and p.endswith(".txt"))
new = sorted(p for p in files if p.startswith("体测报告/新系统已导出/") and p.endswith(".txt"))
assert len(old) == 47 and len(new) == 18
for p in old + new:
    assert files[p].splitlines()[0].startswith("体测报告")
note = files["体测报告/迁移说明.md"]
assert note.splitlines()[0].startswith("# 体测报告归档说明")
assert "9 月 26 日" in note and "10 月 9 日" in note
readme = files["README.md"]
assert readme.splitlines()[0].startswith("# 岳川健身 会员体测归档")
def _both(n):
    if isinstance(n, float):
        return list(dict.fromkeys(["%.2f" % n, "{:,.2f}".format(n)]))
    return list(dict.fromkeys([str(n), "{:,}".format(n)]))
print(json.dumps({"expected_contains_any": _both(len(old))}))
