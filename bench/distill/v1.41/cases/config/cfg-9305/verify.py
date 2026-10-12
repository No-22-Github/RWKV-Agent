# DISTILL-CANARY-1e562fcc : distillation case
import json
case = json.load(open("case.json"))
F = case["files"]
LINES = {'php/fpm.ini': 6, 'php/web.ini': 6, 'php/admin.ini': 6, 'php/cron.ini': 6, 'php/cli.ini': 6, 'php/README.md': 4}
assert sorted(F) == sorted(LINES)
for path, n in LINES.items():
    assert len(F[path].splitlines()) == n, path
assert F['php/README.md'].startswith('# PHP 配置')
def rewrite(path, text):
    if not path.endswith(".ini") or path.endswith("/cli.ini"):
        return None
    new = "\n".join("memory_limit = 256M" if r == "memory_limit = 128M" else r for r in text.split("\n"))
    return new if new != text else None
changed = {}
for path, text in F.items():
    new = rewrite(path, text)
    if new is not None:
        assert new != text, path
        changed[path] = new
assert len(changed) == 4
print(json.dumps({"files": changed}))
