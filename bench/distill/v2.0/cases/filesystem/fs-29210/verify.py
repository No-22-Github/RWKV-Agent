# DISTILL-CANARY-437f11f7 : distillation case
import json
case = json.load(open("case.json"))
LINES = {'文稿库/src/readme.txt': 2, '文稿库/src/notes.txt': 3, '文稿库/src/app.cfg': 2, '文稿库/src/changelog.md': 2, '文稿库/src/already.txt': 2, '文稿库/win/setup.bat': 2, '文稿库/win/run.bat': 2, '文稿库/README.md': 3}
for _p, _n in LINES.items():
    assert len(case["files"][_p].splitlines()) == _n, _p
F = case["files"]
LINES = {'文稿库/src/readme.txt': 2, '文稿库/src/notes.txt': 3, '文稿库/src/app.cfg': 2, '文稿库/src/changelog.md': 2, '文稿库/src/already.txt': 2, '文稿库/win/setup.bat': 2, '文稿库/win/run.bat': 2, '文稿库/README.md': 3}
assert sorted(F) == sorted(LINES)
for path, n in LINES.items():
    assert len(F[path].splitlines()) == n, path
assert F['文稿库/README.md'].startswith('# 文稿库')
def rewrite(path, text):
    if path.startswith("文稿库/win/") or path == "文稿库/README.md":
        return None
    new = text.replace("\r\n", "\n")
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
