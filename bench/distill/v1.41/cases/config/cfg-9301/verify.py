# DISTILL-CANARY-20629f0d : distillation case
import json
case = json.load(open("case.json"))
F = case["files"]
LINES = {'栈/接口/docker-compose.yml': 7, '栈/前台/docker-compose.yml': 7, '栈/后台/docker-compose.yml': 7, '栈/文档/docker-compose.yml': 7, '栈/旧版/docker-compose.yml': 7, '栈/说明.md': 4}
assert sorted(F) == sorted(LINES)
for path, n in LINES.items():
    assert len(F[path].splitlines()) == n, path
assert F['栈/说明.md'].startswith('# 编排说明')
def rewrite(path, text):
    if not path.endswith("/docker-compose.yml") or "/旧版/" in path:
        return None
    new = text.replace('- "8080:', '- "8090:')
    return new if new != text else None
changed = {}
for path, text in F.items():
    new = rewrite(path, text)
    if new is not None:
        assert new != text, path
        changed[path] = new
assert len(changed) == 4
print(json.dumps({"files": changed}))
