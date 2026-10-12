# DISTILL-CANARY-e740edce : distillation case
import json
case = json.load(open("case.json"))
LINES = {'src/main.c': 7, 'src/util.c': 3, 'src/util.h': 3, 'src/net/sock.c': 4, 'src/Makefile': 2, 'src/vendor/zlib.c': 3, 'src/README.txt': 4}
for _p, _n in LINES.items():
    assert len(case["files"][_p].splitlines()) == _n, _p
F = case["files"]
LINES = {'src/main.c': 7, 'src/util.c': 3, 'src/util.h': 3, 'src/net/sock.c': 4, 'src/Makefile': 2, 'src/vendor/zlib.c': 3, 'src/README.txt': 4}
assert sorted(F) == sorted(LINES)
for path, n in LINES.items():
    assert len(F[path].splitlines()) == n, path
assert F['src/README.txt'].startswith('Source notes')
def rewrite(path, text):
    if path.startswith("src/") and (path.endswith(".c") or path.endswith(".h")) and not path.startswith("src/vendor/"):
        new = text.replace("\t", "    ")
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
