# DISTILL-CANARY-f6cab78c : distillation case
import json
case = json.load(open("case.json"))
F = case["files"]
LINES = {'logrotate.d/web日志.conf': 7, 'logrotate.d/支付日志.conf': 7, 'logrotate.d/搜索日志.conf': 7, 'logrotate.d/网关日志.conf': 8, 'logrotate.d/遗留日志.conf': 7, 'logrotate.d/README.md': 4}
assert sorted(F) == sorted(LINES)
for path, n in LINES.items():
    assert len(F[path].splitlines()) == n, path
assert F['logrotate.d/README.md'].startswith('# logrotate.d')
def rewrite(path, text):
    if not path.endswith(".conf") or path.endswith("/遗留日志.conf"):
        return None
    new = text.replace("    compress\n", "    compress\n    delaycompress\n")
    return new if new != text else None
changed = {}
for path, text in F.items():
    new = rewrite(path, text)
    if new is not None:
        assert new != text, path
        changed[path] = new
assert len(changed) == 4
print(json.dumps({"files": changed}))
