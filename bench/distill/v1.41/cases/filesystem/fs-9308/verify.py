# DISTILL-CANARY-83d6bd01 : distillation case
import json
case = json.load(open("case.json"))
F = case["files"]
LINES = {'语言包/zh-CN.properties': 4, '语言包/en-US.properties': 4, '语言包/ja-JP.properties': 4, '语言包/ko-KR.properties': 4, '语言包/旧客户端/zh-CN.properties': 3, '语言包/README.md': 4}
assert sorted(F) == sorted(LINES)
for path, n in LINES.items():
    assert len(F[path].splitlines()) == n, path
assert F['语言包/README.md'].startswith('# 语言包')
def rewrite(path, text):
    if not path.endswith(".properties") or "/旧客户端/" in path:
        return None
    new = "\n".join("btn.cancel=" + r[len("btn.cancle="):] if r.startswith("btn.cancle=") else r for r in text.split("\n"))
    return new if new != text else None
changed = {}
for path, text in F.items():
    new = rewrite(path, text)
    if new is not None:
        assert new != text, path
        changed[path] = new
assert len(changed) == 4
print(json.dumps({"files": changed}))
