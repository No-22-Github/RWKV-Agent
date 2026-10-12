# DISTILL-CANARY-bd563009 : distillation case
import json
case = json.load(open("case.json"))
LINES = {'jobs/sync.toml': 4, 'jobs/report.toml': 4, 'jobs/cleanup.toml': 4, 'jobs/export.toml': 6, 'jobs/nightly.toml': 4, 'jobs/README.md': 5}
for _p, _n in LINES.items():
    assert len(case["files"][_p].splitlines()) == _n, _p
F = case["files"]
LINES = {'jobs/sync.toml': 4, 'jobs/report.toml': 4, 'jobs/cleanup.toml': 4, 'jobs/export.toml': 6, 'jobs/nightly.toml': 4, 'jobs/README.md': 5}
assert sorted(F) == sorted(LINES)
for path, n in LINES.items():
    assert len(F[path].splitlines()) == n, path
assert F['jobs/README.md'].startswith('# 定时任务')
def rewrite(path, text):
    if not path.startswith("jobs/") or not path.endswith(".toml") or path == "jobs/nightly.toml":
        return None
    rows = text.split("\n")
    out, section = [], ""
    for r in rows:
        if r.startswith("["):
            section = r
        out.append("retries = 5" if (r == "retries = 3" and section == "") else r)
    new = "\n".join(out)
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
