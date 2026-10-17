# DISTILL-CANARY-2b01b629 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '5598c6d0601c4d40c10b318586fe25b699d55880ce8ad9841b2d2e40173bf4d9', "fixture changed"
OPS = json.loads('[["sub", "lib/logger.js", "import { nowIso } from \'./clock.js\';", "import { nowUtc } from \'./clock.js\';"], ["sub", "lib/logger.js", "${nowIso()}", "${nowUtc()}"], ["sub", "lib/audit.js", "import { nowIso } from \'./clock.js\';", "import { nowUtc } from \'./clock.js\';"], ["sub", "lib/audit.js", "at: nowIso()", "at: nowUtc()"], ["sub", "lib/clock.js", "export function nowIso() {", "export function nowUtc() {"]]')
end = dict(files)
for _, path, old, new in OPS:
    assert end[path].count(old) == 1, (path, old)
    end[path] = end[path].replace(old, new)
print(json.dumps({"files": {p: t for p, t in end.items() if files[p] != t}}, ensure_ascii=False))
