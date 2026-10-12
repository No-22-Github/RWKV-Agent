# DISTILL-CANARY-00c899c9 : distillation case
import json
case = json.load(open("case.json"))
LINES = {'charts/api/values.yaml': 8, 'charts/web/values.yaml': 5, 'charts/worker/values.yaml': 7, 'charts/cron/values.yaml': 8, 'charts/billing-legacy/values.yaml': 5, 'charts/README.md': 5}
for _p, _n in LINES.items():
    assert len(case["files"][_p].splitlines()) == _n, _p
F = case["files"]
LINES = {'charts/api/values.yaml': 8, 'charts/web/values.yaml': 5, 'charts/worker/values.yaml': 7, 'charts/cron/values.yaml': 8, 'charts/billing-legacy/values.yaml': 5, 'charts/README.md': 5}
assert sorted(F) == sorted(LINES)
for path, n in LINES.items():
    assert len(F[path].splitlines()) == n, path
assert F['charts/README.md'].startswith('# Charts')
def rewrite(path, text):
    if not path.startswith("charts/") or not path.endswith("values.yaml") or "billing-legacy" in path:
        return None
    new = text.replace("\nimage:\n  repo: registry.local/", "\nimage:\n  repo: registry.local/")
    rows = ["  tag: v1.5.0" if r == "  tag: v1.4.2" else r for r in text.split("\n")]
    new = "\n".join(rows)
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
