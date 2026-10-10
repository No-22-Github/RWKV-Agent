# DISTILL-CANARY-1a0c64f4 : distillation case
import json

case = json.load(open("case.json"))
files = case["files"]
old = sorted(p for p in files if p.startswith("归档/巡检报告/旧系统归档/") and p.endswith(".txt"))
new = sorted(p for p in files if p.startswith("归档/巡检报告/新系统已导出/") and p.endswith(".txt"))
assert len(old) == 34 and len(new) == 13
for p in old + new:
    assert files[p].splitlines()[0].startswith("巡检报告") or files[p].splitlines()[0].startswith("专项检查")
note = files["归档/迁移说明.md"]
assert note.splitlines()[0].startswith("# 巡检报告归档迁移说明")
assert "9 月 24 日" in note and "第二批" in note and "10 月 13 日" in note
readme = files["README.md"]
assert readme.splitlines()[0].startswith("# 岳川健身 安全巡检归档")
def _both(n):
    if isinstance(n, float):
        return list(dict.fromkeys(["%.2f" % n, "{:,.2f}".format(n)]))
    return list(dict.fromkeys([str(n), "{:,}".format(n)]))
print(json.dumps({"expected_contains_any": _both(len(old))}))
