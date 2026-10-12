# DISTILL-CANARY-448225f6 : distillation case
import json
case = json.load(open("case.json"))
F = case["files"]
LINES = {'轮转/nginx': 7, '轮转/应用': 7, '轮转/任务': 7, '轮转/邮件': 7, '轮转/审计': 7, '轮转/说明.txt': 5}
assert sorted(F) == sorted(LINES)
for path, n in LINES.items():
    assert len(F[path].splitlines()) == n, path
assert F['轮转/说明.txt'].startswith('日志轮转说明')
def rewrite(path, text):
    if not path.startswith("轮转/") or path.endswith("说明.txt") or path.endswith("/审计"):
        return None
    new = "\n".join("    weekly" if r == "    daily" else r for r in text.split("\n"))
    return new if new != text else None
changed = {}
for path, text in F.items():
    new = rewrite(path, text)
    if new is not None:
        assert new != text, path
        changed[path] = new
assert len(changed) == 4
print(json.dumps({"files": changed}))
