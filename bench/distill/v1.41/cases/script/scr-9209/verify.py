# DISTILL-CANARY-0e4c3f04 : distillation case
import json
case = json.load(open("case.json"))
LINES = {'jobs/ingest.sh': 4, 'jobs/transform.sh': 3, 'jobs/publish.sh': 3, 'jobs/housekeeping.sh': 3, 'jobs/purge-legacy.sh': 3, 'jobs/README.md': 5}
for _p, _n in LINES.items():
    assert len(case["files"][_p].splitlines()) == _n, _p
F = case["files"]
LINES = {'jobs/ingest.sh': 4, 'jobs/transform.sh': 3, 'jobs/publish.sh': 3, 'jobs/housekeeping.sh': 3, 'jobs/purge-legacy.sh': 3, 'jobs/README.md': 5}
assert sorted(F) == sorted(LINES)
for path, n in LINES.items():
    assert len(F[path].splitlines()) == n, path
assert F['jobs/README.md'].startswith('# 作业脚本')
def rewrite(path, text):
    if path.startswith("jobs/") and path.endswith(".sh") and path != "jobs/purge-legacy.sh":
        new = text.replace("/tmp/work/", "/var/tmp/work/")
        return new if new != text else None
    return None

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
