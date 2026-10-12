# DISTILL-CANARY-76efe133 : distillation case
import json
case = json.load(open("case.json"))
LINES = {'conf/app.properties': 4, 'conf/worker.properties': 4, 'conf/gateway.properties': 4, 'conf/batch.properties': 4, 'conf/audit.properties': 4, 'conf/README.txt': 4}
for _p, _n in LINES.items():
    assert len(case["files"][_p].splitlines()) == _n, _p
F = case["files"]
LINES = {'conf/app.properties': 4, 'conf/worker.properties': 4, 'conf/gateway.properties': 4, 'conf/batch.properties': 4, 'conf/audit.properties': 4, 'conf/README.txt': 4}
assert sorted(F) == sorted(LINES)
for path, n in LINES.items():
    assert len(F[path].splitlines()) == n, path
assert F['conf/README.txt'].startswith('Logging notes')
def rewrite(path, text):
    if not path.startswith("conf/") or not path.endswith(".properties") or path == "conf/audit.properties":
        return None
    new = text.replace("\nlog4j.rootLogger=INFO,", "\nlog4j.rootLogger=WARN,")
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
