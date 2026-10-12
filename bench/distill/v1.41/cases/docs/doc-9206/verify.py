# DISTILL-CANARY-1df74727 : distillation case
import json
case = json.load(open("case.json"))
LINES = {'nginx/conf.d/site-a.conf': 4, 'nginx/conf.d/site-b.conf': 4, 'nginx/conf.d/site-c.conf': 4, 'nginx/conf.d/api.conf': 4, 'nginx/generated/auto.conf': 4, 'nginx/nginx.conf.default': 2, 'nginx/README.md': 5}
for _p, _n in LINES.items():
    assert len(case["files"][_p].splitlines()) == _n, _p
F = case["files"]
LINES = {'nginx/conf.d/site-a.conf': 4, 'nginx/conf.d/site-b.conf': 4, 'nginx/conf.d/site-c.conf': 4, 'nginx/conf.d/api.conf': 4, 'nginx/generated/auto.conf': 4, 'nginx/nginx.conf.default': 2, 'nginx/README.md': 5}
assert sorted(F) == sorted(LINES)
for path, n in LINES.items():
    assert len(F[path].splitlines()) == n, path
assert F['nginx/README.md'].startswith('# Nginx 配置')
def rewrite(path, text):
    if path.startswith("nginx/") and path.endswith(".conf") and not path.startswith("nginx/generated/"):
        return text + "# managed by ops-team\n"
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
