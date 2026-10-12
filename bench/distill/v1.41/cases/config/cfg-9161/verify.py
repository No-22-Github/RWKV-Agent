# DISTILL-CANARY-3f665d0b : distillation case
import json
case = json.load(open("case.json"))
F = case["files"]
LINES = {'conf/api.ini': 6, 'conf/web.ini': 7, 'conf/worker.ini': 6, 'conf/cron.ini': 7, 'conf/mailer.ini': 6, 'conf/local.ini': 6, 'conf/README.md': 4}
assert sorted(F) == sorted(LINES)
for path, n in LINES.items():
    assert len(F[path].splitlines()) == n, path
assert F['conf/README.md'].startswith('# 配置说明')
def rewrite(path, text):
    if not path.startswith("conf/") or not path.endswith(".ini") or path == "conf/local.ini":
        return None
    new = "\n".join("request_timeout = " + r[len("timeout = "):] if r.startswith("timeout = ") else r for r in text.split("\n"))
    return new if new != text else None
changed = {}
for path, text in F.items():
    new = rewrite(path, text)
    if new is not None:
        assert new != text, path
        changed[path] = new
assert len(changed) == 5
print(json.dumps({"files": changed}))
