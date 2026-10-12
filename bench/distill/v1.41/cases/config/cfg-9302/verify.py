# DISTILL-CANARY-aa590143 : distillation case
import json
case = json.load(open("case.json"))
F = case["files"]
LINES = {'基础设施/缓存/compose.yaml': 7, '基础设施/会话/compose.yaml': 7, '基础设施/队列/compose.yaml': 7, '基础设施/限流/compose.yaml': 7, '基础设施/测试旧环境/compose.yaml': 7, '基础设施/README.md': 4}
assert sorted(F) == sorted(LINES)
for path, n in LINES.items():
    assert len(F[path].splitlines()) == n, path
assert F['基础设施/README.md'].startswith('# 基础设施')
def rewrite(path, text):
    if not path.endswith("/compose.yaml") or "/测试旧环境/" in path:
        return None
    new = text.replace("image: redis:6.2-alpine", "image: redis:7.2-alpine")
    return new if new != text else None
changed = {}
for path, text in F.items():
    new = rewrite(path, text)
    if new is not None:
        assert new != text, path
        changed[path] = new
assert len(changed) == 4
print(json.dumps({"files": changed}))
