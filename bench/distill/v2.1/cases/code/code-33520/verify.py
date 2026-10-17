# DISTILL-CANARY-feea1d29 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '137297024e3f0405bcf8f463cdecfc79b83a7c147a83e781b455295afb6f2fdd', "fixture changed"
OPS = json.loads('[["sub", "src/jobs/mail.js", "bus.emit({ type: \'mail\', job });", "bus.emit({ type: \'mail\', job, at: Date.now() });"], ["sub", "src/jobs/sms.js", "emit({ type: \'sms\', job });", "emit({ type: \'sms\', job, at: Date.now() });"]]')
end = dict(files)
for _, path, old, new in OPS:
    assert end[path].count(old) == 1, (path, old)
    end[path] = end[path].replace(old, new)
print(json.dumps({"files": {p: t for p, t in end.items() if files[p] != t}}, ensure_ascii=False))
