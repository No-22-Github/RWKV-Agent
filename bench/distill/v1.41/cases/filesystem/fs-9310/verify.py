# DISTILL-CANARY-8d04e783 : distillation case
import json
case = json.load(open("case.json"))
F = case["files"]
LINES = {'db/migrations/001_init.sql': 2, 'db/migrations/002_add_status.sql': 2, 'db/migrations/003_archive.sql': 2, 'db/migrations/004_views.sql': 2, 'db/migrations/005_fk.sql': 1, 'db/README.md': 4}
assert sorted(F) == sorted(LINES)
for path, n in LINES.items():
    assert len(F[path].splitlines()) == n, path
assert F['db/README.md'].startswith('# 数据库迁移')
import re
def rewrite(path, text):
    if not path.startswith("db/migrations/") or path.endswith("001_init.sql"):
        return None
    new = re.sub(r"\borders\b", "sales_orders", text)
    return new if new != text else None
changed = {}
for path, text in F.items():
    new = rewrite(path, text)
    if new is not None:
        assert new != text, path
        changed[path] = new
assert len(changed) == 4
print(json.dumps({"files": changed}))
