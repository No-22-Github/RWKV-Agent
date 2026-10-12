# DISTILL-CANARY-28a35a32 : distillation case
import json
case = json.load(open("case.json"))
LINES = {'env/dev.env': 5, 'env/test.env': 5, 'env/staging.env': 5, 'env/qa.env': 5, 'env/prod.env': 5, 'env/README.md': 4}
for _p, _n in LINES.items():
    assert len(case["files"][_p].splitlines()) == _n, _p
F = case["files"]
LINES = {'env/dev.env': 5, 'env/test.env': 5, 'env/staging.env': 5, 'env/qa.env': 5, 'env/prod.env': 5, 'env/README.md': 4}
assert sorted(F) == sorted(LINES)
for path, n in LINES.items():
    assert len(F[path].splitlines()) == n, path
assert F['env/README.md'].startswith('# 环境变量说明')
def rewrite(path, text):
    if not path.startswith("env/") or not path.endswith(".env") or path == "env/prod.env":
        return None
    new = text.replace("\nDB_HOST=db-old.internal\n", "\nDB_HOST=db-new.internal\n")
    return new if new != text else None

def plan(files):
    out = {}
    for path, text in files.items():
        new = rewrite(path, text)
        out[path] = text if new is None else new
    return out

final = plan(F)
changed = {p: t for p, t in final.items() if F.get(p) != t}
removed = [p for p in F if p not in final]
assert len(changed) + len(removed) == 4
print(json.dumps({"files": changed}))
