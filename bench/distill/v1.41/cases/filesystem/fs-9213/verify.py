# DISTILL-CANARY-da7bdfd4 : distillation case
import json
case = json.load(open("case.json"))
LINES = {'repo/src/a.c.orig': 1, 'repo/src/a.c.rej': 1, 'repo/src/net/b.h.orig': 1, 'repo/src/net/c.c.rej': 1, 'repo/src/a.c': 1, 'repo/src/net/b.h': 1, 'repo/src/net/c.c': 1, 'repo/third_party/zstd/zstd.c.orig': 1, 'repo/third_party/zstd/patch.rej': 1, 'repo/src/ORIGIN.md': 3, 'repo/README.md': 5}
for _p, _n in LINES.items():
    assert len(case["files"][_p].splitlines()) == _n, _p
F = case["files"]
LINES = {'repo/src/a.c.orig': 1, 'repo/src/a.c.rej': 1, 'repo/src/net/b.h.orig': 1, 'repo/src/net/c.c.rej': 1, 'repo/src/a.c': 1, 'repo/src/net/b.h': 1, 'repo/src/net/c.c': 1, 'repo/third_party/zstd/zstd.c.orig': 1, 'repo/third_party/zstd/patch.rej': 1, 'repo/src/ORIGIN.md': 3, 'repo/README.md': 5}
assert sorted(F) == sorted(LINES)
for path, n in LINES.items():
    assert len(F[path].splitlines()) == n, path
assert F['repo/README.md'].startswith('# Repo')
def plan(files):
    return {p: t for p, t in files.items() if not ((p.endswith(".orig") or p.endswith(".rej")) and not p.startswith("repo/third_party/"))}
final = plan(F)
changed = {p: t for p, t in final.items() if F.get(p) != t}
removed = [p for p in F if p not in final]
assert len(changed) + len(removed) == 4
print(json.dumps({"files": changed}))
