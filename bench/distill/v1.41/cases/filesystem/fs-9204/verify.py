# DISTILL-CANARY-3b23527b : distillation case
import json
case = json.load(open("case.json"))
LINES = {'notes/会议-0901.markdown': 3, 'notes/会议-0908.markdown': 3, 'notes/会议-0915.markdown': 3, 'notes/周报/总结.markdown': 3, 'notes/归档/旧会议.markdown': 3, 'notes/会议-0901.markdown.bak': 1, 'notes/README.txt': 5}
for _p, _n in LINES.items():
    assert len(case["files"][_p].splitlines()) == _n, _p
F = case["files"]
LINES = {'notes/会议-0901.markdown': 3, 'notes/会议-0908.markdown': 3, 'notes/会议-0915.markdown': 3, 'notes/周报/总结.markdown': 3, 'notes/归档/旧会议.markdown': 3, 'notes/会议-0901.markdown.bak': 1, 'notes/README.txt': 5}
assert sorted(F) == sorted(LINES)
for path, n in LINES.items():
    assert len(F[path].splitlines()) == n, path
assert F['notes/README.txt'].startswith('笔记目录说明')
def plan(files):
    out = {}
    for path, text in files.items():
        if path.endswith(".markdown") and not path.startswith("notes/归档/"):
            out[path[: -len(".markdown")] + ".md"] = text
        else:
            out[path] = text
    return out
final = plan(F)
changed = {p: t for p, t in final.items() if F.get(p) != t}
removed = [p for p in F if p not in final]
assert len(changed) + len(removed) == 8
print(json.dumps({"files": changed}))
