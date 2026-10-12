# DISTILL-CANARY-b2240a09 : distillation case
import json
case = json.load(open("case.json"))
F = case["files"]
LINES = {'数据库/视图/用户视图.sql': 4, '数据库/视图/订单视图.sql': 4, '数据库/视图/库存视图.sql': 4, '数据库/视图/报表视图.sql': 4, '数据库/视图/pg_dump备份.sql': 2, '数据库/说明.md': 4}
assert sorted(F) == sorted(LINES)
for path, n in LINES.items():
    assert len(F[path].splitlines()) == n, path
assert F['数据库/说明.md'].startswith('# 视图说明')
def rewrite(path, text):
    if not path.startswith("数据库/视图/") or path.endswith("pg_dump备份.sql"):
        return None
    new = text.replace("public.", "app.")
    return new if new != text else None
changed = {}
for path, text in F.items():
    new = rewrite(path, text)
    if new is not None:
        assert new != text, path
        changed[path] = new
assert len(changed) == 4
print(json.dumps({"files": changed}))
